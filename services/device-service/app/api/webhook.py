"""
Webhook API for Rule Engine Integration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.device import Device
from app.schemas.device import WebhookControlRequest, WebhookControlResponse
from app.services.command_queue import CommandQueue
from app.services.websocket_manager import websocket_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["webhook"])


@router.post("/control", response_model=WebhookControlResponse)
async def webhook_control(
    request: WebhookControlRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for Rule Engine to send device control commands
    
    This endpoint is called by the Rule Engine when a DEVICE_CONTROL action is triggered.
    """
    logger.info(f"Received webhook control request: {request.dict()}")
    
    # Verify device exists and belongs to workspace
    result = await db.execute(
        select(Device).where(
            Device.id == request.device_id,
            Device.workspace_id == request.workspace_id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device {request.device_id} not found in workspace {request.workspace_id}"
        )
    
    # Create command
    command = await CommandQueue.create_command(
        db=db,
        device_id=request.device_id,
        command_type=request.command_type,
        parameters=request.parameters
    )
    
    logger.info(f"Created command {command.id} for device {request.device_id}")
    
    # Try to send to device if it's connected
    if websocket_manager.is_device_connected(request.device_id):
        command_dict = {
            "command_id": command.id,
            "command_type": command.command_type,
            "parameters": command.parameters
        }
        
        success = await websocket_manager.send_command(request.device_id, command_dict)
        
        if success:
            await CommandQueue.mark_command_sent(db, command.id)
            status = "sent"
            message = f"Command sent to device {device.name}"
            logger.info(f"Command {command.id} sent to connected device {request.device_id}")
        else:
            status = "pending"
            message = f"Command queued for device {device.name} (connection lost)"
            logger.warning(f"Failed to send command {command.id} to device {request.device_id}")
    else:
        status = "pending"
        message = f"Command queued for device {device.name} (offline)"
        logger.info(f"Command {command.id} queued for offline device {request.device_id}")
    
    return WebhookControlResponse(
        command_id=command.id,
        status=status,
        message=message
    )
