"""
Client Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.schemas.client import ClientRegister, ClientResponse, ClientToken, ClientUpdate
from app.models.client import Client
from app.models.device import Device
import secrets
import jwt
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/api/clients", tags=["clients"])

# TODO: Move to config
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


@router.post("/register", response_model=ClientToken)
async def register_client(
    client_data: ClientRegister,
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
    db: Session = Depends(get_db)
):
    """
    Register a new PC Client
    
    Returns client_id and JWT token for WebSocket authentication
    """
    # Create client ID
    client_id = f"client-{secrets.token_hex(8)}"
    
    # Create client record
    client = Client(
        id=client_id,
        workspace_id=workspace_id,
        name=client_data.name,
        client_type=client_data.client_type,
        os=client_data.os,
        version=client_data.version,
        status="offline",
        client_metadata=client_data.client_metadata
    )
    
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    # Generate JWT token for WebSocket auth
    token_payload = {
        "client_id": client_id,
        "workspace_id": workspace_id,
        "exp": datetime.utcnow() + timedelta(days=365)
    }
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return ClientToken(
        client_id=client_id,
        client_token=token,
        workspace_id=workspace_id
    )


@router.get("", response_model=List[ClientResponse])
async def list_clients(
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
    db: Session = Depends(get_db)
):
    """
    List all clients in workspace
    """
    stmt = select(Client).where(Client.workspace_id == workspace_id)
    result = await db.execute(stmt)
    clients = result.scalars().all()
    
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
    db: Session = Depends(get_db)
):
    """
    Get client details
    """
    stmt = select(Client).where(
        Client.id == client_id,
        Client.workspace_id == workspace_id
    )
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_update: ClientUpdate,
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
    db: Session = Depends(get_db)
):
    """
    Update client details
    """
    stmt = select(Client).where(
        Client.id == client_id,
        Client.workspace_id == workspace_id
    )
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update fields
    if client_update.name is not None:
        client.name = client_update.name
    if client_update.client_metadata is not None:
        client.client_metadata = client_update.client_metadata
    
    client.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(client)
    
    return client


@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
    db: Session = Depends(get_db)
):
    """
    Delete client and its devices
    """
    stmt = select(Client).where(
        Client.id == client_id,
        Client.workspace_id == workspace_id
    )
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Delete associated devices
    device_stmt = select(Device).where(Device.client_id == client_id)
    device_result = await db.execute(device_stmt)
    devices = device_result.scalars().all()
    
    for device in devices:
        db.delete(device)
    
    # Delete client
    db.delete(client)
    await db.commit()
    
    return {"message": "Client deleted successfully"}
