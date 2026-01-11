"""
Client Message Handlers - Process messages from PC Clients
"""
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def handle_heartbeat(client_id: str, message: dict, db: AsyncSession):
    """
    Handle heartbeat message from client
    
    Args:
        client_id: Client ID
        message: Heartbeat message
        db: Database session
    """
    try:
        from app.models.client import Client
        from sqlalchemy import select, update
        
        # Update last_seen timestamp
        stmt = (
            update(Client)
            .where(Client.id == client_id)
            .values(last_seen=datetime.utcnow())
        )
        await db.execute(stmt)
        await db.commit()
        
        logger.debug(f"Heartbeat received from client {client_id}")
    except Exception as e:
        logger.error(f"Error handling heartbeat from client {client_id}: {e}")


async def handle_command_result(client_id: str, message: dict, db: AsyncSession):
    """
    Handle command execution result from client
    
    Args:
        client_id: Client ID
        message: Result message with command_id, status, result
        db: Database session
    """
    try:
        from app.models.device import DeviceCommand, CommandStatus
        from sqlalchemy import select, update
        
        command_id = message.get("command_id")
        status = message.get("status", "completed")
        result = message.get("result", {})
        error = message.get("error")
        
        if not command_id:
            logger.warning(f"Command result from client {client_id} missing command_id")
            return
        
        # Map status strings to enum
        status_map = {
            "completed": CommandStatus.COMPLETED,
            "failed": CommandStatus.FAILED,
            "success": CommandStatus.COMPLETED,
            "error": CommandStatus.FAILED
        }
        
        db_status = status_map.get(status, CommandStatus.COMPLETED)
        
        # Update command in database
        stmt = (
            update(DeviceCommand)
            .where(DeviceCommand.id == command_id)
            .values(
                status=db_status,
                result=result if status == "completed" else None,
                error=error if status == "failed" else None,
                executed_at=datetime.utcnow()
            )
        )
        
        await db.execute(stmt)
        await db.commit()
        
        logger.info(f"Command {command_id} {status} by client {client_id}")
        
    except Exception as e:
        logger.error(f"Error handling command result from client {client_id}: {e}")


async def handle_client_error(client_id: str, message: dict, db: AsyncSession):
    """
    Handle error report from client
    
    Args:
        client_id: Client ID
        message: Error message with error_code, message, device_id
        db: Database session
    """
    try:
        error_code = message.get("error_code", "UNKNOWN")
        error_message = message.get("message", "No message")
        device_id = message.get("device_id")
        
        logger.error(
            f"Client {client_id} reported error: {error_code} - {error_message}"
            + (f" (device: {device_id})" if device_id else "")
        )
        
        # TODO: Store errors in database for monitoring
        # TODO: Send notification to user/admin
        
    except Exception as e:
        logger.error(f"Error handling client error from {client_id}: {e}")


async def handle_device_discovery(client_id: str, message: dict, db: AsyncSession):
    """
    Handle device discovery report from client
    
    Args:
        client_id: Client ID
        message: Discovery message with list of discovered devices
        db: Database session
    """
    try:
        devices = message.get("devices", [])
        
        logger.info(f"Client {client_id} discovered {len(devices)} devices: {devices}")
        
        # TODO: Auto-register discovered devices
        # TODO: Update device connection parameters
        
    except Exception as e:
        logger.error(f"Error handling device discovery from client {client_id}: {e}")
