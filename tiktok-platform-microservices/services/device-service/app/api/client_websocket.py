"""
WebSocket API for PC Client Connections
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.client_connection_manager import client_manager
from app.services.client_message_handlers import (
    handle_heartbeat,
    handle_command_result,
    handle_client_error,
    handle_device_discovery
)
from app.models.client import Client
import jwt
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["client-websocket"])

# JWT Configuration (should be moved to environment variables)
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"


async def authenticate_client(token: str, db: AsyncSession) -> Client:
    """
    Authenticate client from JWT token
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        Client object if valid, None otherwise
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        client_id = payload.get("client_id")
        workspace_id = payload.get("workspace_id")
        
        if not client_id or not workspace_id:
            logger.warning("JWT token missing client_id or workspace_id")
            return None
        
        # Get client from database
        from sqlalchemy import select
        
        stmt = select(Client).where(
            Client.id == client_id,
            Client.workspace_id == workspace_id
        )
        result = await db.execute(stmt)
        client = result.scalar_one_or_none()
        
        if not client:
            logger.warning(f"Client {client_id} not found in database")
            return None
        
        return client
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error authenticating client: {e}")
        return None


@router.websocket("/ws/client/{client_token}")
async def client_websocket(
    websocket: WebSocket,
    client_token: str
):
    """
    WebSocket endpoint for PC Client connections
    
    Clients connect using their JWT token.
    Once connected, they receive pending commands and can send:
    - Heartbeat messages
    - Command execution results
    - Error reports
    - Device discovery updates
    
    Message format from server to client:
    {
        "type": "device_command",
        "command_id": "uuid",
        "device_id": "device-xyz",
        "command_type": "turn_on|turn_off|set_brightness|custom",
        "parameters": {...}
    }
    
    Message format from client to server:
    {
        "type": "heartbeat|result|error|device_discovered",
        ...type-specific fields...
    }
    """
    # Get database session
    async with get_db().__anext__() as db:
        # Authenticate client
        client = await authenticate_client(client_token, db)
        
        if not client:
            logger.warning(f"Invalid token attempted connection")
            await websocket.close(code=4001, reason="Invalid authentication token")
            return
        
        client_id = client.id
        workspace_id = client.workspace_id
        logger.info(f"Client {client_id} ({client.name}) attempting to connect")
        
        # Connect client (this accepts the WebSocket)
        await client_manager.connect(client_id, workspace_id, websocket, db)
        
        try:
            # Send pending commands to client
            from app.services.client_command_queue import ClientCommandQueue
            
            sent_count = await ClientCommandQueue.send_pending_commands_to_client(
                client_id, websocket, db
            )
            
            if sent_count > 0:
                logger.info(f"Sent {sent_count} pending commands to client {client_id}")
            
            # Listen for messages from client
            while True:
                # Receive message
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    logger.debug(f"Received message from client {client_id}: {message_type}")
                    
                    # Route message to appropriate handler
                    if message_type == "heartbeat":
                        await handle_heartbeat(client_id, message, db)
                        # Send pong response
                        await websocket.send_json({"type": "pong"})
                    
                    elif message_type == "result":
                        await handle_command_result(client_id, message, db)
                    
                    elif message_type == "error":
                        await handle_client_error(client_id, message, db)
                    
                    elif message_type == "device_discovered":
                        await handle_device_discovery(client_id, message, db)
                    
                    else:
                        logger.warning(f"Unknown message type from client {client_id}: {message_type}")
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client {client_id}: {data}")
                except Exception as e:
                    logger.error(f"Error processing message from client {client_id}: {e}")
        
        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected normally")
        
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
        
        finally:
            # Cleanup
            await client_manager.disconnect(client_id, db)
            logger.info(f"Client {client_id} connection closed")
