"""
WebSocket API for Device Connections
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.device_manager import DeviceManager
from app.services.command_queue import CommandQueue
from app.services.websocket_manager import websocket_manager
from app.models.device import DeviceStatus
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/device/{token}")
async def device_websocket(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for device connections
    
    Devices connect using their authentication token.
    Once connected, they receive pending commands and can send command results.
    
    Message format from server to device:
    {
        "command_id": "uuid",
        "command_type": "turn_on|turn_off|set_brightness|custom",
        "parameters": {...}
    }
    
    Message format from device to server:
    {
        "command_id": "uuid",
        "status": "completed|failed",
        "result": {...},  // optional
        "error": "error message"  // optional, for failed commands
    }
    """
    # Get database session
    async with get_db().__anext__() as db:
        # Authenticate device
        device = await DeviceManager.get_device_by_token(db, token)
        
        if not device:
            logger.warning(f"Invalid token attempted connection: {token[:8]}...")
            await websocket.close(code=1008, reason="Invalid authentication token")
            return
        
        device_id = device.id
        logger.info(f"Device {device_id} ({device.name}) attempting to connect")
        
        # Accept connection
        await websocket.accept()
        
        # Register connection
        await websocket_manager.register_connection(device_id, websocket)
        
        # Update device status to online
        await DeviceManager.update_device_status(db, device_id, DeviceStatus.ONLINE)
        
        try:
            # Send pending commands
            pending_commands = await CommandQueue.get_pending_commands(db, device_id)
            
            for command in pending_commands:
                command_dict = {
                    "command_id": command.id,
                    "command_type": command.command_type,
                    "parameters": command.parameters
                }
                
                await websocket.send_json(command_dict)
                await CommandQueue.mark_command_sent(db, command.id)
                logger.info(f"Sent pending command {command.id} to device {device_id}")
            
            # Listen for messages from device
            while True:
                # Receive message
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    logger.info(f"Received message from device {device_id}: {message}")
                    
                    # Handle command result
                    if "command_id" in message:
                        command_id = message["command_id"]
                        status = message.get("status", "completed")
                        
                        if status == "completed":
                            result = message.get("result", {})
                            await CommandQueue.mark_command_completed(db, command_id, result)
                            logger.info(f"Command {command_id} completed successfully")
                        
                        elif status == "failed":
                            error = message.get("error", "Unknown error")
                            await CommandQueue.mark_command_failed(db, command_id, error)
                            logger.error(f"Command {command_id} failed: {error}")
                    
                    # Handle heartbeat/ping
                    elif message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                        await DeviceManager.update_device_status(db, device_id, DeviceStatus.ONLINE)
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from device {device_id}: {data}")
                except Exception as e:
                    logger.error(f"Error processing message from device {device_id}: {e}")
        
        except WebSocketDisconnect:
            logger.info(f"Device {device_id} disconnected normally")
        
        except Exception as e:
            logger.error(f"WebSocket error for device {device_id}: {e}")
        
        finally:
            # Cleanup
            await websocket_manager.unregister_connection(device_id)
            await DeviceManager.update_device_status(db, device_id, DeviceStatus.OFFLINE)
            logger.info(f"Device {device_id} connection closed")
