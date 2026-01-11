"""
Device models for IoT device management
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class DeviceType(str, enum.Enum):
    """Device types"""
    ARDUINO = "arduino"
    ESP32 = "esp32"
    RASPBERRY_PI = "raspberry_pi"
    VIRTUAL = "virtual"


class DeviceStatus(str, enum.Enum):
    """Device status"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class CommandStatus(str, enum.Enum):
    """Command execution status"""
    PENDING = "pending"
    SENT = "sent"
    COMPLETED = "completed"
    FAILED = "failed"


class Device(Base):
    """IoT Device model"""
    __tablename__ = "devices"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenancy
    workspace_id = Column(String, nullable=False, index=True)
    
    # Device Info
    name = Column(String, nullable=False)
    device_type = Column(
        SQLEnum(DeviceType, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    
    # Status
    status = Column(
        SQLEnum(DeviceStatus, values_callable=lambda x: [e.value for e in x]),
        default=DeviceStatus.OFFLINE,
        nullable=False,
        index=True
    )
    
    # Authentication
    agent_token_hash = Column(String, nullable=False, unique=True)
    
    # Connection Info
    last_seen = Column(DateTime(timezone=True))
    
    # Custom Properties
    device_metadata = Column(JSON, default={})
    
    # PC Client Integration (NEW)
    client_id = Column(String, ForeignKey("clients.id"))
    connection_type = Column(String)  # "serial", "bluetooth", "usb", "wifi"
    connection_params = Column(JSON)  # {"port": "COM3", "baudrate": 9600}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    commands = relationship("DeviceCommand", back_populates="device", cascade="all, delete-orphan")
    states = relationship("DeviceState", back_populates="device", cascade="all, delete-orphan")
    client = relationship("Client", back_populates="devices")
    
    def __repr__(self):
        return f"<Device(id={self.id}, name={self.name}, status={self.status})>"


class DeviceCommand(Base):
    """Device command queue"""
    __tablename__ = "device_commands"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key
    device_id = Column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Command Info
    command_type = Column(String, nullable=False)  # turn_on, turn_off, set_brightness, custom
    parameters = Column(JSON, default={})
    
    # Status
    status = Column(
        SQLEnum(CommandStatus, values_callable=lambda x: [e.value for e in x]),
        default=CommandStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Result
    result = Column(JSON)
    error_message = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationship
    device = relationship("Device", back_populates="commands")
    
    def __repr__(self):
        return f"<DeviceCommand(id={self.id}, type={self.command_type}, status={self.status})>"


class DeviceState(Base):
    """Device state history"""
    __tablename__ = "device_states"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key
    device_id = Column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # State Data
    state_data = Column(JSON, nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship
    device = relationship("Device", back_populates="states")
    
    def __repr__(self):
        return f"<DeviceState(device_id={self.device_id}, timestamp={self.timestamp})>"
