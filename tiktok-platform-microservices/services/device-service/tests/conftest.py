"""
Test configuration and fixtures for device service tests
"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db
from app.models.client import Client, ClientStatus
from app.models.device import Device, DeviceType, DeviceStatus

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5435/device_db_test"

# JWT configuration (same as in client_websocket.py)
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"


# Async engine for tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for tests"""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create FastAPI test client with database override"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_workspace(db_session: AsyncSession) -> str:
    """Create test workspace and return workspace_id"""
    # For now, just return a test workspace ID
    # In a real scenario, you'd create a workspace in the database
    return "test-workspace-123"


@pytest.fixture
async def test_client_registered(
    db_session: AsyncSession,
    test_workspace: str
) -> dict:
    """Create and register a test client, return client data with JWT token"""
    # Create client
    client = Client(
        workspace_id=test_workspace,
        name="Test PC Client",
        client_type="desktop",
        status=ClientStatus.OFFLINE
    )
    
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    
    # Generate JWT token
    token_data = {
        "client_id": client.id,
        "workspace_id": client.workspace_id,
        "exp": datetime.utcnow() + timedelta(days=365)
    }
    token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        "id": client.id,
        "workspace_id": client.workspace_id,
        "name": client.name,
        "client_type": client.client_type,
        "status": client.status,
        "token": token
    }


@pytest.fixture
async def test_device(
    db_session: AsyncSession,
    test_workspace: str,
    test_client_registered: dict
) -> Device:
    """Create test device linked to test client"""
    device = Device(
        workspace_id=test_workspace,
        name="Test Device",
        device_type=DeviceType.LIGHT,
        status=DeviceStatus.OFFLINE,
        client_id=test_client_registered["id"],
        connection_type="serial",
        connection_params={"port": "/dev/ttyUSB0", "baudrate": 9600}
    )
    
    db_session.add(device)
    await db_session.commit()
    await db_session.refresh(device)
    
    return device


@pytest.fixture
def auth_headers(test_workspace: str) -> dict:
    """Create authentication headers for API requests"""
    return {
        "X-Workspace-ID": test_workspace
    }
