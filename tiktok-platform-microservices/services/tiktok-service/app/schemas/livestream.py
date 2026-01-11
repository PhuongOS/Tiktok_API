"""
Livestream API schemas
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.livestream import LivestreamStatus
from app.utils.tiktok_parser import TikTokInputParser


class LivestreamConnect(BaseModel):
    """Connect request"""
    tiktok_input: str = Field(
        ...,
        description="Username, room ID, or TikTok LIVE URL",
        examples=["@charlidamelio", "7123456789012345678", "https://www.tiktok.com/@user/live"]
    )
    
    @field_validator('tiktok_input')
    @classmethod
    def validate_input(cls, v: str) -> str:
        TikTokInputParser.parse(v)  # Raises ValueError if invalid
        return v


class LivestreamResponse(BaseModel):
    """Livestream response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    workspace_id: str
    tiktok_username: str
    room_id: Optional[str]
    status: LivestreamStatus
    
    # Statistics
    total_comments: int
    total_gifts: int
    total_likes: int
    total_joins: int
    total_follows: int
    total_shares: int
    total_events: int
    
    # Timestamps
    connected_at: Optional[datetime]
    disconnected_at: Optional[datetime]
    created_at: datetime
