from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ClientStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    client_type = Column(String)  # "desktop", "laptop"
    os = Column(String)  # "Windows", "Mac", "Linux"
    version = Column(String)  # Client software version
    status = Column(String, default="offline")  # "online", "offline", "error"
    last_seen = Column(DateTime)
    ip_address = Column(String)
    client_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationship to devices
    devices = relationship("Device", back_populates="client")
