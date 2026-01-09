"""
Unit tests for authentication endpoints
"""
import pytest


class TestUserRegistration:
    """Test user registration"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, client):
        """Test successful user registration"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "password": "password123"
        }
        
        # First registration
        response1 = await client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Duplicate registration
        response2 = await client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "123"  # Too short
            }
        )
        
        assert response.status_code == 422


class TestUserLogin:
    """Test user login"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user_data):
        """Test successful login"""
        # Register user first
        await client.post("/api/auth/register", json=test_user_data)
        
        # Login
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user_data):
        """Test login with wrong password"""
        # Register user
        await client.post("/api/auth/register", json=test_user_data)
        
        # Login with wrong password
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["email"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


class TestGetCurrentUser:
    """Test get current user endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, authenticated_client, test_user_data):
        """Test getting current user with valid token"""
        response = await authenticated_client.get("/api/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        client.headers["Authorization"] = "Bearer invalid_token"
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401


class TestWorkspaceManagement:
    """Test workspace management"""
    
    @pytest.mark.asyncio
    async def test_create_workspace(self, authenticated_client):
        """Test creating a workspace"""
        response = await authenticated_client.post(
            "/api/auth/workspaces",
            json={
                "name": "My Workspace",
                "plan_tier": "free"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Workspace"
        assert data["plan_tier"] == "free"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_list_workspaces(self, authenticated_client):
        """Test listing user's workspaces"""
        # Create a workspace
        await authenticated_client.post(
            "/api/auth/workspaces",
            json={"name": "Test Workspace", "plan_tier": "free"}
        )
        
        # List workspaces
        response = await authenticated_client.get("/api/auth/workspaces")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["name"] == "Test Workspace"


# Run with: pytest tests/test_auth.py -v
