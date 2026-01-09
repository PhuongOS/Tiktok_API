"""
Device REST API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.device import Device, DeviceCommand
from app.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceWithToken,
    CommandCreate,
    CommandResponse,
)
from app.services.device_manager import DeviceManager
from app.services.command_queue import CommandQueue
from app.services.websocket_manager import websocket_manager

router = APIRouter(prefix="/api/devices", tags=["devices"])


# Dependency to get workspace_id from header
async def get_current_workspace(request: Request) -> str:
    """Get workspace ID from X-Workspace-ID header"""
    workspace_id = request.headers.get("X-Workspace-ID")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header is required")
    return workspace_id


@router.post("", response_model=DeviceWithToken, status_code=201)
async def create_device(
    device_data: DeviceCreate,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new device
    
    Returns the device with authentication token.
    **Save the token** - it will not be shown again!
    """
    device, token = await DeviceManager.create_device(
        db=db,
        workspace_id=workspace_id,
        name=device_data.name,
        device_type=device_data.device_type,
        metadata=device_data.metadata
    )
    
    # Convert to response model
    device_dict = {
        "id": device.id,
        "workspace_id": device.workspace_id,
        "name": device.name,
        "device_type": device.device_type,
        "status": device.status,
        "last_seen": device.last_seen,
        "device_metadata": device.device_metadata,
        "created_at": device.created_at,
        "updated_at": device.updated_at,
        "token": token
    }
    
    return DeviceWithToken(**device_dict)


@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    List all devices in the workspace
    """
    result = await db.execute(
        select(Device).where(Device.workspace_id == workspace_id)
    )
    devices = result.scalars().all()
    
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Get device details
    """
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.workspace_id == workspace_id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return device


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Update device information
    """
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.workspace_id == workspace_id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Update fields
    if device_data.name is not None:
        device.name = device_data.name
    if device_data.metadata is not None:
        device.device_metadata = device_data.metadata
    
    await db.commit()
    await db.refresh(device)
    
    return device


@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a device
    """
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.workspace_id == workspace_id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    await db.delete(device)
    await db.commit()
    
    return None


@router.post("/{device_id}/control", response_model=CommandResponse, status_code=201)
async def send_control_command(
    device_id: str,
    command_data: CommandCreate,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a control command to a device
    
    The command will be queued and sent to the device when it's online.
    """
    # Verify device exists and belongs to workspace
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.workspace_id == workspace_id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Create command
    command = await CommandQueue.create_command(
        db=db,
        device_id=device_id,
        command_type=command_data.command_type,
        parameters=command_data.parameters
    )
    
    # Try to send to device if it's connected
    if websocket_manager.is_device_connected(device_id):
        command_dict = {
            "command_id": command.id,
            "command_type": command.command_type,
            "parameters": command.parameters
        }
        
        success = await websocket_manager.send_command(device_id, command_dict)
        if success:
            await CommandQueue.mark_command_sent(db, command.id)
            await db.refresh(command)
    
    return command


@router.get("/{device_id}/commands", response_model=List[CommandResponse])
async def get_command_history(
    device_id: str,
    workspace_id: str = Depends(get_current_workspace),
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Get command history for a device
    """
    # Verify device exists and belongs to workspace
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.workspace_id == workspace_id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    commands = await CommandQueue.get_command_history(db, device_id, limit)
    
    return commands


@router.get("/{device_id}/commands/{command_id}", response_model=CommandResponse)
async def get_command_details(
    device_id: str,
    command_id: str,
    workspace_id: str = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Get command details
    """
    # Verify device exists and belongs to workspace
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.workspace_id == workspace_id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get command
    result = await db.execute(
        select(DeviceCommand).where(
            DeviceCommand.id == command_id,
            DeviceCommand.device_id == device_id
        )
    )
    command = result.scalar_one_or_none()
    
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return command
