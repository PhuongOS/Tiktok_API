"""
Device Manager Service - Token generation and device management
"""
import secrets
import hashlib
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.device import Device, DeviceStatus
from datetime import datetime


class DeviceManager:
    """Device management service"""
    
    @staticmethod
    def generate_device_token(length: int = 32) -> str:
        """
        Generate a secure random token for device authentication
        
        Args:
            length: Token length in bytes (default 32)
            
        Returns:
            Hex-encoded token string
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash a token for secure storage
        
        Args:
            token: Plain token string
            
        Returns:
            SHA256 hash of the token
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def verify_token(token: str, token_hash: str) -> bool:
        """
        Verify a token against its hash
        
        Args:
            token: Plain token string
            token_hash: Stored hash
            
        Returns:
            True if token matches hash
        """
        return DeviceManager.hash_token(token) == token_hash
    
    @staticmethod
    async def create_device(
        db: AsyncSession,
        workspace_id: str,
        name: str,
        device_type: str,
        metadata: dict = None
    ) -> tuple[Device, str]:
        """
        Create a new device with authentication token
        
        Args:
            db: Database session
            workspace_id: Workspace ID
            name: Device name
            device_type: Device type
            metadata: Custom device properties
            
        Returns:
            Tuple of (Device, plain_token)
        """
        # Generate token
        plain_token = DeviceManager.generate_device_token()
        token_hash = DeviceManager.hash_token(plain_token)
        
        # Create device
        device = Device(
            workspace_id=workspace_id,
            name=name,
            device_type=device_type,
            agent_token_hash=token_hash,
            device_metadata=metadata or {},
            status=DeviceStatus.OFFLINE
        )
        
        db.add(device)
        await db.commit()
        await db.refresh(device)
        
        return device, plain_token
    
    @staticmethod
    async def get_device_by_token(db: AsyncSession, token: str) -> Optional[Device]:
        """
        Get device by authentication token
        
        Args:
            db: Database session
            token: Plain token string
            
        Returns:
            Device if found and token is valid, None otherwise
        """
        token_hash = DeviceManager.hash_token(token)
        
        result = await db.execute(
            select(Device).where(Device.agent_token_hash == token_hash)
        )
        device = result.scalar_one_or_none()
        
        return device
    
    @staticmethod
    async def update_device_status(
        db: AsyncSession,
        device_id: str,
        status: DeviceStatus,
        update_last_seen: bool = True
    ) -> Optional[Device]:
        """
        Update device status and optionally last_seen timestamp
        
        Args:
            db: Database session
            device_id: Device ID
            status: New status
            update_last_seen: Whether to update last_seen timestamp
            
        Returns:
            Updated device or None if not found
        """
        result = await db.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        
        if device:
            device.status = status
            if update_last_seen:
                device.last_seen = datetime.utcnow()
            
            await db.commit()
            await db.refresh(device)
        
        return device
