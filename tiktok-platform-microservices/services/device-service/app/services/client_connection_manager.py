"""
Client Connection Manager - Manage WebSocket connections for PC Clients
"""
from typing import Dict, List, Optional
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ClientConnectionManager:
    """
    Singleton WebSocket connection manager for PC Clients
    Maintains active client connections and workspace mappings
    """
    
    def __init__(self):
        # Dictionary mapping client_id to WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        # Dictionary mapping client_id to workspace_id for filtering
        self.client_workspaces: Dict[str, str] = {}
    
    async def connect(self, client_id: str, workspace_id: str, websocket: WebSocket, db: AsyncSession):
        """
        Accept and register a new client connection
        
        Args:
            client_id: Client ID
            workspace_id: Workspace ID
            websocket: WebSocket connection
            db: Database session
        """
        # Close existing connection if any
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].close()
                logger.warning(f"Closed existing connection for client {client_id}")
            except Exception as e:
                logger.warning(f"Error closing existing connection for client {client_id}: {e}")
        
        # Accept WebSocket connection
        await websocket.accept()
        
        # Register connection
        self.active_connections[client_id] = websocket
        self.client_workspaces[client_id] = workspace_id
        
        # Update client status in database
        await self.update_client_status(client_id, "online", db)
        
        logger.info(f"Client {client_id} connected. Total client connections: {len(self.active_connections)}")
    
    async def disconnect(self, client_id: str, db: AsyncSession):
        """
        Unregister a client connection and update status
        
        Args:
            client_id: Client ID
            db: Database session
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        if client_id in self.client_workspaces:
            del self.client_workspaces[client_id]
        
        # Update client status in database
        await self.update_client_status(client_id, "offline", db)
        
        logger.info(f"Client {client_id} disconnected. Total client connections: {len(self.active_connections)}")
    
    async def send_command(self, client_id: str, command: dict) -> bool:
        """
        Send command to a specific client
        
        Args:
            client_id: Client ID
            command: Command data (will be sent as JSON)
            
        Returns:
            True if command was sent successfully, False otherwise
        """
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} is not connected")
            return False
        
        try:
            websocket = self.active_connections[client_id]
            await websocket.send_json(command)
            logger.info(f"Command sent to client {client_id}: {command.get('type')}")
            return True
        except Exception as e:
            logger.error(f"Error sending command to client {client_id}: {e}")
            return False
    
    async def broadcast_to_workspace(self, workspace_id: str, message: dict):
        """
        Broadcast a message to all clients in a workspace
        
        Args:
            workspace_id: Workspace ID
            message: Message data
        """
        sent_count = 0
        
        for client_id, ws_id in self.client_workspaces.items():
            if ws_id == workspace_id and client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {e}")
        
        logger.info(f"Broadcast to workspace {workspace_id}: sent to {sent_count} clients")
    
    async def update_client_status(self, client_id: str, status: str, db: AsyncSession):
        """
        Update client status and last_seen in database
        
        Args:
            client_id: Client ID
            status: Status ("online" or "offline")
            db: Database session
        """
        try:
            from app.models.client import Client
            
            # Get client
            result = await db.execute(
                f"SELECT * FROM clients WHERE id = '{client_id}'"
            )
            client = result.first()
            
            if client:
                # Update using raw SQL for now (will be improved)
                await db.execute(
                    f"UPDATE clients SET status = '{status}', last_seen = NOW() WHERE id = '{client_id}'"
                )
                await db.commit()
                logger.debug(f"Updated client {client_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating client status: {e}")
    
    def is_online(self, client_id: str) -> bool:
        """
        Check if a client is currently connected
        
        Args:
            client_id: Client ID
            
        Returns:
            True if client is connected
        """
        return client_id in self.active_connections
    
    def get_online_clients(self, workspace_id: str) -> List[str]:
        """
        Get list of online client IDs in a workspace
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of client IDs
        """
        return [
            client_id 
            for client_id, ws_id in self.client_workspaces.items() 
            if ws_id == workspace_id
        ]
    
    def get_connection_count(self) -> int:
        """
        Get the number of active client connections
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
    
    def get_all_online_clients(self) -> List[str]:
        """
        Get list of all online client IDs
        
        Returns:
            List of client IDs
        """
        return list(self.active_connections.keys())


# Global singleton instance
client_manager = ClientConnectionManager()
