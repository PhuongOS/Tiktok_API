"""
Livestream API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import logging

from app.database import get_db
from app.models.livestream import Livestream, LivestreamStatus
from app.schemas.livestream import LivestreamConnect, LivestreamResponse
from app.services.tiktok_client import tiktok_manager
from app.services.redis_publisher import redis_publisher
from app.utils.tiktok_parser import TikTokInputParser

router = APIRouter(prefix="/api/livestreams", tags=["Livestreams"])
logger = logging.getLogger(__name__)


# TODO: Get from Auth Service JWT
async def get_current_workspace() -> str:
    return "workspace-123"

async def get_current_user() -> str:
    return "user-123"


@router.post("/connect", response_model=LivestreamResponse, status_code=201)
async def connect_livestream(
    data: LivestreamConnect,
    workspace_id: str = Depends(get_current_workspace),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect to TikTok LIVE
    
    Accepts: username, room ID, or URL
    """
    # Parse input
    try:
        input_type, value = TikTokInputParser.parse(data.tiktok_input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create record
    livestream = Livestream(
        workspace_id=workspace_id,
        created_by=user_id,
        tiktok_username=value,
        status=LivestreamStatus.CONNECTING
    )
    
    db.add(livestream)
    await db.commit()
    await db.refresh(livestream)
    
    # Event callback
    async def on_event(event_type: str, event_data: dict):
        try:
            # Update status
            if event_type == "connect":
                livestream.status = LivestreamStatus.LIVE
                livestream.room_id = event_data.get("room_id")
                livestream.connected_at = datetime.utcnow()
            elif event_type in ["disconnect", "live_end"]:
                livestream.status = LivestreamStatus.DISCONNECTED
                livestream.disconnected_at = datetime.utcnow()
            
            # Update stats
            if event_type == "comment":
                livestream.total_comments += 1
            elif event_type == "gift":
                livestream.total_gifts += 1
            elif event_type == "like":
                livestream.total_likes += 1
            elif event_type == "join":
                livestream.total_joins += 1
            elif event_type == "follow":
                livestream.total_follows += 1
            elif event_type == "share":
                livestream.total_shares += 1
            
            livestream.total_events += 1
            await db.commit()
            
            # Publish to Redis
            await redis_publisher.publish_event(
                workspace_id=workspace_id,
                event_type=event_type,
                event_data=event_data
            )
        except Exception as e:
            logger.error(f"Event error: {e}")
    
    # Connect
    try:
        if input_type == 'username':
            await tiktok_manager.connect(
                livestream_id=livestream.id,
                unique_id=value,
                event_callback=on_event
            )
        elif input_type == 'room_id':
            await tiktok_manager.connect(
                livestream_id=livestream.id,
                room_id=value,
                event_callback=on_event
            )
        else:  # short_url
            await tiktok_manager.connect(
                livestream_id=livestream.id,
                unique_id=value,
                event_callback=on_event
            )
    except Exception as e:
        livestream.status = LivestreamStatus.ERROR
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")
    
    return livestream


@router.post("/{livestream_id}/disconnect")
async def disconnect_livestream(
    livestream_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect from stream"""
    result = await db.execute(
        select(Livestream).where(
            Livestream.id == livestream_id,
            Livestream.workspace_id == workspace_id
        )
    )
    livestream = result.scalar_one_or_none()
    
    if not livestream:
        raise HTTPException(status_code=404, detail="Not found")
    
    try:
        await tiktok_manager.disconnect(livestream_id)
        livestream.status = LivestreamStatus.DISCONNECTED
        livestream.disconnected_at = datetime.utcnow()
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message": "Disconnected"}


@router.get("", response_model=List[LivestreamResponse])
async def list_livestreams(
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List all livestreams"""
    result = await db.execute(
        select(Livestream)
        .where(Livestream.workspace_id == workspace_id)
        .order_by(Livestream.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{livestream_id}", response_model=LivestreamResponse)
async def get_livestream(
    livestream_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Get livestream details"""
    result = await db.execute(
        select(Livestream).where(
            Livestream.id == livestream_id,
            Livestream.workspace_id == workspace_id
        )
    )
    livestream = result.scalar_one_or_none()
    
    if not livestream:
        raise HTTPException(status_code=404, detail="Not found")
    
    return livestream
