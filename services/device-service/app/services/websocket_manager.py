"""
WebSocket Manager - Manage WebSocket connections for devices
"""
from typing import Dict, Optional
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Singleton WebSocket connection manager
    Maintains active device connections
    """
    
    def __init__(self):
        # Dictionary mapping device_id to WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def register_connection(self, device_id: str, websocket: WebSocket):
        """
        Register a new device connection
        
        Args:
            device_id: Device ID
            websocket: WebSocket connection
        """
        # Close existing connection if any
        if device_id in self.active_connections:
            try:
                await self.active_connections[device_id].close()
            except Exception as e:
                logger.warning(f"Error closing existing connection for device {device_id}: {e}")
        
        self.active_connections[device_id] = websocket
        logger.info(f"Device {device_id} connected. Total connections: {len(self.active_connections)}")
    
    async def unregister_connection(self, device_id: str):
        """
        Unregister a device connection
        
        Args:
            device_id: Device ID
        """
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            logger.info(f"Device {device_id} disconnected. Total connections: {len(self.active_connections)}")
    
    def is_device_connected(self, device_id: str) -> bool:
        """
        Check if a device is currently connected
        
        Args:
            device_id: Device ID
            
        Returns:
            True if device is connected
        """
        return device_id in self.active_connections
    
    async def send_command(self, device_id: str, command: dict) -> bool:
        """
        Send a command to a specific device
        
        Args:
            device_id: Device ID
            command: Command data (will be sent as JSON)
            
        Returns:
            True if command was sent successfully, False otherwise
        """
        if device_id not in self.active_connections:
            logger.warning(f"Device {device_id} is not connected")
            return False
        
        try:
            websocket = self.active_connections[device_id]
            await websocket.send_json(command)
            logger.info(f"Command sent to device {device_id}: {command.get('command_type')}")
            return True
        except Exception as e:
            logger.error(f"Error sending command to device {device_id}: {e}")
            # Remove broken connection
            await self.unregister_connection(device_id)
            return False
    
    async def broadcast_to_workspace(self, workspace_id: str, message: dict):
        """
        Broadcast a message to all devices in a workspace
        (Future feature - requires workspace tracking)
        
        Args:
            workspace_id: Workspace ID
            message: Message data
        """
        # TODO: Implement workspace tracking
        logger.info(f"Broadcast to workspace {workspace_id}: {message}")
    
    def get_connection_count(self) -> int:
        """
        Get the number of active connections
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
    
    def get_connected_devices(self) -> list:
        """
        Get list of connected device IDs
        
        Returns:
            List of device IDs
        """
        return list(self.active_connections.keys())


# Global singleton instance
websocket_manager = WebSocketManager()
