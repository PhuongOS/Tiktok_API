"""
Database configuration for Rule Engine Service
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Database URL from environment or default to PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://rules_user:rules_password@localhost:5434/rules_db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Alias for consumer usage (who context manages it manually)
async_session_factory = AsyncSessionLocal

# Base class for models
Base = declarative_base()


async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        yield session
