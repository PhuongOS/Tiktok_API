"""
Client Command Queue Service - Manage commands for PC Clients
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.device import DeviceCommand, CommandStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ClientCommandQueue:
    """
    Command queue management for PC Clients
    Handles queuing commands when clients are offline
    """
    
    @staticmethod
    async def get_pending_commands_for_client(
        db: AsyncSession,
        client_id: str
    ) -> List[DeviceCommand]:
        """
        Get all pending commands for devices connected to a specific client
        
        Args:
            db: Database session
            client_id: Client ID
            
        Returns:
            List of pending commands
        """
        from app.models.device import Device
        
        # Get all devices for this client
        result = await db.execute(
            select(Device).where(Device.client_id == client_id)
        )
        devices = result.scalars().all()
        device_ids = [d.id for d in devices]
        
        if not device_ids:
            return []
        
        # Get pending commands for these devices
        result = await db.execute(
            select(DeviceCommand)
            .where(
                DeviceCommand.device_id.in_(device_ids),
                DeviceCommand.status == CommandStatus.PENDING
            )
            .order_by(DeviceCommand.created_at)
        )
        
        return result.scalars().all()
    
    @staticmethod
    async def queue_command_for_offline_client(
        db: AsyncSession,
        device_id: str,
        command_type: str,
        parameters: dict = None
    ) -> DeviceCommand:
        """
        Queue a command for a device whose client is offline
        
        Args:
            db: Database session
            device_id: Device ID
            command_type: Command type
            parameters: Command parameters
            
        Returns:
            Created command
        """
        command = DeviceCommand(
            device_id=device_id,
            command_type=command_type,
            parameters=parameters or {},
            status=CommandStatus.PENDING
        )
        
        db.add(command)
        await db.commit()
        await db.refresh(command)
        
        logger.info(f"Queued command {command.id} for offline client (device: {device_id})")
        
        return command
    
    @staticmethod
    async def send_pending_commands_to_client(
        client_id: str,
        websocket,
        db: AsyncSession
    ) -> int:
        """
        Send all pending commands to a client that just connected
        
        Args:
            client_id: Client ID
            websocket: WebSocket connection
            db: Database session
            
        Returns:
            Number of commands sent
        """
        pending_commands = await ClientCommandQueue.get_pending_commands_for_client(db, client_id)
        
        sent_count = 0
        for command in pending_commands:
            try:
                command_dict = {
                    "type": "device_command",
                    "command_id": command.id,
                    "device_id": command.device_id,
                    "command_type": command.command_type,
                    "parameters": command.parameters
                }
                
                await websocket.send_json(command_dict)
                
                # Mark as sent
                command.status = CommandStatus.SENT
                command.sent_at = datetime.utcnow()
                sent_count += 1
                
                logger.info(f"Sent pending command {command.id} to client {client_id}")
                
            except Exception as e:
                logger.error(f"Error sending command {command.id} to client {client_id}: {e}")
        
        if sent_count > 0:
            await db.commit()
        
        return sent_count
