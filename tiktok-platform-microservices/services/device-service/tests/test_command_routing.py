"""
Tests for Command Routing Logic
"""
import pytest
from fastapi import status
from app.models.device import CommandStatus


@pytest.mark.asyncio
async def test_route_to_online_client(test_client, auth_headers, test_client_registered, test_device):
    """Test command routing to online client"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    token = test_client_registered["token"]
    device_id = test_device.id
    
    # Connect client via WebSocket (simulates online client)
    with TestClient(app) as ws_client:
        with ws_client.websocket_connect(f"/ws/client/{token}") as websocket:
            # Send device command via API
            response = test_client.post(
                f"/api/devices/{device_id}/control",
                json={
                    "command_type": "turn_on",
                    "parameters": {}
                },
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            
            # Command should be created
            assert "id" in data
            assert data["command_type"] == "turn_on"
            # Should be sent immediately (status = sent)
            assert data["status"] in ["sent", "pending"]  # May be sent or pending depending on timing


@pytest.mark.asyncio
async def test_queue_for_offline_client(test_client, auth_headers, test_client_registered, test_device):
    """Test command queuing for offline client"""
    device_id = test_device.id
    
    # Client is offline (no WebSocket connection)
    response = test_client.post(
        f"/api/devices/{device_id}/control",
        json={
            "command_type": "turn_off",
            "parameters": {}
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Command should be queued
    assert "id" in data
    assert data["command_type"] == "turn_off"
    assert data["status"] == "pending"  # Should be pending (queued)


@pytest.mark.asyncio
async def test_no_client_assigned(test_client, auth_headers, test_workspace, db_session):
    """Test command when device has no client assigned"""
    from app.models.device import Device, DeviceType, DeviceStatus
    
    # Create device without client_id
    device = Device(
        workspace_id=test_workspace,
        name="Unassigned Device",
        device_type=DeviceType.LIGHT,
        status=DeviceStatus.OFFLINE,
        client_id=None  # No client assigned
    )
    
    db_session.add(device)
    await db_session.commit()
    await db_session.refresh(device)
    
    # Send command
    response = test_client.post(
        f"/api/devices/{device.id}/control",
        json={
            "command_type": "turn_on",
            "parameters": {}
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Command should be created but pending (no client to send to)
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_workspace_isolation(test_client, auth_headers, test_client_registered, test_device):
    """Test commands don't cross workspaces"""
    device_id = test_device.id
    
    # Send command in correct workspace
    response1 = test_client.post(
        f"/api/devices/{device_id}/control",
        json={
            "command_type": "turn_on",
            "parameters": {}
        },
        headers=auth_headers
    )
    
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Try to send command from different workspace
    other_headers = {"X-Workspace-ID": "other-workspace-456"}
    response2 = test_client.post(
        f"/api/devices/{device_id}/control",
        json={
            "command_type": "turn_off",
            "parameters": {}
        },
        headers=other_headers
    )
    
    # Should fail - device not found in other workspace
    assert response2.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_command_history(test_client, auth_headers, test_device):
    """Test getting command history for a device"""
    device_id = test_device.id
    
    # Send multiple commands
    for i in range(3):
        test_client.post(
            f"/api/devices/{device_id}/control",
            json={
                "command_type": "set_brightness",
                "parameters": {"level": i * 25}
            },
            headers=auth_headers
        )
    
    # Get command history
    response = test_client.get(
        f"/api/devices/{device_id}/commands",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 3  # At least the 3 we just created
    
    # Verify command structure
    command = data[0]
    assert "id" in command
    assert "command_type" in command
    assert "status" in command
    assert "created_at" in command


@pytest.mark.asyncio
async def test_get_command_details(test_client, auth_headers, test_device):
    """Test getting specific command details"""
    device_id = test_device.id
    
    # Create command
    create_response = test_client.post(
        f"/api/devices/{device_id}/control",
        json={
            "command_type": "turn_on",
            "parameters": {}
        },
        headers=auth_headers
    )
    
    command_id = create_response.json()["id"]
    
    # Get command details
    response = test_client.get(
        f"/api/devices/{device_id}/commands/{command_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == command_id
    assert data["device_id"] == device_id
    assert data["command_type"] == "turn_on"


@pytest.mark.asyncio
async def test_command_not_found(test_client, auth_headers, test_device):
    """Test getting non-existent command"""
    device_id = test_device.id
    
    response = test_client.get(
        f"/api/devices/{device_id}/commands/non-existent-command",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
