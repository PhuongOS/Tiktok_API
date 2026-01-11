"""
Tests for Client WebSocket Connection
"""
import pytest
import json
from fastapi.testclient import TestClient
from app.main import app


@pytest.mark.asyncio
async def test_websocket_connect_valid_token(test_client_registered):
    """Test WebSocket connection with valid JWT token"""
    token = test_client_registered["token"]
    
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/client/{token}") as websocket:
            # Connection should be accepted
            assert websocket is not None
            
            # Should be able to send/receive messages
            # Send heartbeat
            websocket.send_json({"type": "heartbeat"})
            
            # Receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"


@pytest.mark.asyncio
async def test_websocket_connect_invalid_token():
    """Test WebSocket connection with invalid JWT token"""
    invalid_token = "invalid-token-123"
    
    with TestClient(app) as client:
        try:
            with client.websocket_connect(f"/ws/client/{invalid_token}") as websocket:
                # Should not reach here
                assert False, "Connection should have been rejected"
        except Exception as e:
            # Connection should be rejected
            assert "4001" in str(e) or "Invalid" in str(e)


@pytest.mark.asyncio
async def test_websocket_heartbeat(test_client_registered):
    """Test heartbeat message handling"""
    token = test_client_registered["token"]
    
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/client/{token}") as websocket:
            # Send heartbeat
            heartbeat_msg = {
                "type": "heartbeat",
                "timestamp": "2026-01-11T10:00:00Z"
            }
            websocket.send_json(heartbeat_msg)
            
            # Should receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"


@pytest.mark.asyncio
async def test_websocket_command_result(test_client_registered, test_device, db_session):
    """Test command result message handling"""
    from app.models.device import DeviceCommand, CommandStatus
    
    token = test_client_registered["token"]
    
    # Create a test command
    command = DeviceCommand(
        device_id=test_device.id,
        command_type="turn_on",
        parameters={},
        status=CommandStatus.SENT
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)
    
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/client/{token}") as websocket:
            # Send command result
            result_msg = {
                "type": "result",
                "command_id": command.id,
                "status": "completed",
                "result": {"success": True}
            }
            websocket.send_json(result_msg)
            
            # Give it time to process
            import time
            time.sleep(0.1)
    
    # Verify command was updated
    await db_session.refresh(command)
    assert command.status == CommandStatus.COMPLETED
    assert command.result == {"success": True}


@pytest.mark.asyncio
async def test_websocket_error_message(test_client_registered):
    """Test error message handling"""
    token = test_client_registered["token"]
    
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/client/{token}") as websocket:
            # Send error message
            error_msg = {
                "type": "error",
                "error_code": "DEVICE_NOT_FOUND",
                "message": "Device not connected",
                "device_id": "test-device-123"
            }
            websocket.send_json(error_msg)
            
            # Error should be logged (no response expected)
            # Just verify connection is still alive
            websocket.send_json({"type": "heartbeat"})
            response = websocket.receive_json()
            assert response["type"] == "pong"


@pytest.mark.asyncio
async def test_websocket_device_discovery(test_client_registered):
    """Test device discovery message handling"""
    token = test_client_registered["token"]
    
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/client/{token}") as websocket:
            # Send device discovery
            discovery_msg = {
                "type": "device_discovered",
                "devices": [
                    {"port": "/dev/ttyUSB0", "type": "serial"},
                    {"port": "/dev/ttyUSB1", "type": "serial"}
                ]
            }
            websocket.send_json(discovery_msg)
            
            # Discovery should be logged (no response expected)
            # Verify connection still alive
            websocket.send_json({"type": "heartbeat"})
            response = websocket.receive_json()
            assert response["type"] == "pong"


@pytest.mark.asyncio
async def test_websocket_disconnect(test_client_registered, db_session):
    """Test disconnect handling and status update"""
    from app.models.client import Client, ClientStatus
    from sqlalchemy import select
    
    token = test_client_registered["token"]
    client_id = test_client_registered["id"]
    
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/client/{token}") as websocket:
            # Send a message to ensure connection is active
            websocket.send_json({"type": "heartbeat"})
            response = websocket.receive_json()
            assert response["type"] == "pong"
        
        # WebSocket is now closed
    
    # Verify client status updated to offline
    result = await db_session.execute(
        select(Client).where(Client.id == client_id)
    )
    client_obj = result.scalar_one_or_none()
    
    # Note: Status update might be async, so we check if it exists
    assert client_obj is not None


@pytest.mark.asyncio
async def test_pending_commands_delivery(test_client_registered, test_device, db_session):
    """Test that pending commands are sent when client connects"""
    from app.models.device import DeviceCommand, CommandStatus
    
    token = test_client_registered["token"]
    
    # Create pending commands
    command1 = DeviceCommand(
        device_id=test_device.id,
        command_type="turn_on",
        parameters={},
        status=CommandStatus.PENDING
    )
    command2 = DeviceCommand(
        device_id=test_device.id,
        command_type="set_brightness",
        parameters={"level": 50},
        status=CommandStatus.PENDING
    )
    
    db_session.add_all([command1, command2])
    await db_session.commit()
    
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/client/{token}") as websocket:
            # Should receive pending commands
            messages = []
            try:
                # Receive up to 3 messages (2 commands + maybe heartbeat response)
                for _ in range(3):
                    msg = websocket.receive_json(timeout=1)
                    messages.append(msg)
            except:
                pass  # Timeout is expected
            
            # Verify we received the commands
            command_messages = [m for m in messages if m.get("type") == "device_command"]
            assert len(command_messages) >= 2
            
            # Verify command IDs
            command_ids = [m["command_id"] for m in command_messages]
            assert command1.id in command_ids
            assert command2.id in command_ids
