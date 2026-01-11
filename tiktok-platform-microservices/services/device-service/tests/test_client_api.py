"""
Tests for Client Management API
"""
import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_register_client(test_client, auth_headers):
    """Test POST /api/clients/register - Register new PC client"""
    response = test_client.post(
        "/api/clients/register",
        json={
            "name": "My PC Client",
            "client_type": "desktop"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Verify response structure
    assert "id" in data
    assert "token" in data
    assert data["name"] == "My PC Client"
    assert data["client_type"] == "desktop"
    assert data["status"] == "offline"
    assert data["workspace_id"] == auth_headers["X-Workspace-ID"]
    
    # Verify token is a valid string
    assert isinstance(data["token"], str)
    assert len(data["token"]) > 50  # JWT tokens are long


@pytest.mark.asyncio
async def test_register_client_missing_workspace(test_client):
    """Test registration without workspace header"""
    response = test_client.post(
        "/api/clients/register",
        json={
            "name": "My PC Client",
            "client_type": "desktop"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_list_clients(test_client, auth_headers, test_client_registered):
    """Test GET /api/clients - List all clients"""
    response = test_client.get(
        "/api/clients",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1  # At least the test client
    
    # Verify client structure
    client = data[0]
    assert "id" in client
    assert "name" in client
    assert "status" in client
    assert "workspace_id" in client


@pytest.mark.asyncio
async def test_list_clients_workspace_isolation(test_client, auth_headers, test_client_registered):
    """Test that clients are isolated by workspace"""
    # Get clients in test workspace
    response1 = test_client.get(
        "/api/clients",
        headers=auth_headers
    )
    
    # Get clients in different workspace
    other_headers = {"X-Workspace-ID": "other-workspace-456"}
    response2 = test_client.get(
        "/api/clients",
        headers=other_headers
    )
    
    assert response1.status_code == status.HTTP_200_OK
    assert response2.status_code == status.HTTP_200_OK
    
    # Different workspaces should have different clients
    data1 = response1.json()
    data2 = response2.json()
    
    # Test workspace should have the registered client
    assert len(data1) >= 1
    # Other workspace should be empty
    assert len(data2) == 0


@pytest.mark.asyncio
async def test_get_client(test_client, auth_headers, test_client_registered):
    """Test GET /api/clients/{id} - Get client details"""
    client_id = test_client_registered["id"]
    
    response = test_client.get(
        f"/api/clients/{client_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == client_id
    assert data["name"] == test_client_registered["name"]
    assert data["client_type"] == test_client_registered["client_type"]


@pytest.mark.asyncio
async def test_get_client_not_found(test_client, auth_headers):
    """Test GET /api/clients/{id} with non-existent ID"""
    response = test_client.get(
        "/api/clients/non-existent-id",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_client(test_client, auth_headers, test_client_registered):
    """Test PATCH /api/clients/{id} - Update client"""
    client_id = test_client_registered["id"]
    
    response = test_client.patch(
        f"/api/clients/{client_id}",
        json={"name": "Updated Client Name"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == client_id
    assert data["name"] == "Updated Client Name"
    
    # Verify changes persisted
    get_response = test_client.get(
        f"/api/clients/{client_id}",
        headers=auth_headers
    )
    assert get_response.json()["name"] == "Updated Client Name"


@pytest.mark.asyncio
async def test_delete_client(test_client, auth_headers, test_client_registered):
    """Test DELETE /api/clients/{id} - Delete client"""
    client_id = test_client_registered["id"]
    
    response = test_client.delete(
        f"/api/clients/{client_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify client is deleted
    get_response = test_client.get(
        f"/api/clients/{client_id}",
        headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_client_not_found(test_client, auth_headers):
    """Test DELETE /api/clients/{id} with non-existent ID"""
    response = test_client.delete(
        "/api/clients/non-existent-id",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
