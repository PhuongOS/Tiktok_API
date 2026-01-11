"""
TikTok LIVE stream session model
"""
from sqlalchemy import Column, String, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class LivestreamStatus(str, enum.Enum):
    """Livestream connection status"""
    CONNECTING = "connecting"
    LIVE = "live"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class Livestream(Base):
    """TikTok LIVE stream session with real-time statistics"""
    __tablename__ = "livestreams"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenancy
    workspace_id = Column(String, nullable=False, index=True)
    created_by = Column(String, nullable=False)  # User ID from Auth Service
    
    # TikTok Info
    tiktok_username = Column(String, nullable=False, index=True)
    room_id = Column(String, nullable=True)  # From ConnectEvent
    
    # Connection Status
    status = Column(
        SQLEnum(LivestreamStatus, values_callable=lambda x: [e.value for e in x]),
        default=LivestreamStatus.CONNECTING,
        nullable=False,
        index=True
    )
    
    # Real-time Statistics
    total_comments = Column(Integer, default=0)
    total_gifts = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_joins = Column(Integer, default=0)
    total_follows = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_events = Column(Integer, default=0)
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True))
    disconnected_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Livestream(id={self.id}, username={self.tiktok_username}, status={self.status})>"
