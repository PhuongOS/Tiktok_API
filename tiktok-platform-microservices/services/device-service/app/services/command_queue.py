"""
Command Queue Service - Command management and execution tracking
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.device import DeviceCommand, CommandStatus
from datetime import datetime


class CommandQueue:
    """Command queue management service"""
    
    @staticmethod
    async def create_command(
        db: AsyncSession,
        device_id: str,
        command_type: str,
        parameters: dict = None
    ) -> DeviceCommand:
        """
        Create a new command in the queue
        
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
        
        return command
    
    @staticmethod
    async def get_pending_commands(
        db: AsyncSession,
        device_id: str
    ) -> List[DeviceCommand]:
        """
        Get all pending commands for a device
        
        Args:
            db: Database session
            device_id: Device ID
            
        Returns:
            List of pending commands
        """
        result = await db.execute(
            select(DeviceCommand)
            .where(
                DeviceCommand.device_id == device_id,
                DeviceCommand.status == CommandStatus.PENDING
            )
            .order_by(DeviceCommand.created_at)
        )
        
        return result.scalars().all()
    
    @staticmethod
    async def mark_command_sent(
        db: AsyncSession,
        command_id: str
    ) -> Optional[DeviceCommand]:
        """
        Mark command as sent to device
        
        Args:
            db: Database session
            command_id: Command ID
            
        Returns:
            Updated command or None if not found
        """
        result = await db.execute(
            select(DeviceCommand).where(DeviceCommand.id == command_id)
        )
        command = result.scalar_one_or_none()
        
        if command:
            command.status = CommandStatus.SENT
            command.sent_at = datetime.utcnow()
            await db.commit()
            await db.refresh(command)
        
        return command
    
    @staticmethod
    async def mark_command_completed(
        db: AsyncSession,
        command_id: str,
        result: dict = None
    ) -> Optional[DeviceCommand]:
        """
        Mark command as completed with result
        
        Args:
            db: Database session
            command_id: Command ID
            result: Command execution result
            
        Returns:
            Updated command or None if not found
        """
        result_data = await db.execute(
            select(DeviceCommand).where(DeviceCommand.id == command_id)
        )
        command = result_data.scalar_one_or_none()
        
        if command:
            command.status = CommandStatus.COMPLETED
            command.result = result or {}
            command.completed_at = datetime.utcnow()
            await db.commit()
            await db.refresh(command)
        
        return command
    
    @staticmethod
    async def mark_command_failed(
        db: AsyncSession,
        command_id: str,
        error_message: str
    ) -> Optional[DeviceCommand]:
        """
        Mark command as failed with error message
        
        Args:
            db: Database session
            command_id: Command ID
            error_message: Error message
            
        Returns:
            Updated command or None if not found
        """
        result = await db.execute(
            select(DeviceCommand).where(DeviceCommand.id == command_id)
        )
        command = result.scalar_one_or_none()
        
        if command:
            command.status = CommandStatus.FAILED
            command.error_message = error_message
            command.completed_at = datetime.utcnow()
            await db.commit()
            await db.refresh(command)
        
        return command
    
    @staticmethod
    async def get_command_history(
        db: AsyncSession,
        device_id: str,
        limit: int = 50
    ) -> List[DeviceCommand]:
        """
        Get command history for a device
        
        Args:
            db: Database session
            device_id: Device ID
            limit: Maximum number of commands to return
            
        Returns:
            List of commands ordered by creation time (newest first)
        """
        result = await db.execute(
            select(DeviceCommand)
            .where(DeviceCommand.device_id == device_id)
            .order_by(DeviceCommand.created_at.desc())
            .limit(limit)
        )
        
        return result.scalars().all()
