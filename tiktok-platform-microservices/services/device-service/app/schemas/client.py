"""
Client schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class ClientRegister(BaseModel):
    """Schema for client registration"""
    name: str
    client_type: Optional[str] = "desktop"
    os: Optional[str] = None
    version: Optional[str] = "1.0.0"
    client_metadata: Optional[Dict] = {}


class ClientResponse(BaseModel):
    """Schema for client response"""
    id: str
    workspace_id: str
    name: str
    client_type: Optional[str]
    os: Optional[str]
    version: Optional[str]
    status: str
    last_seen: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClientToken(BaseModel):
    """Schema for client token response"""
    client_id: str
    client_token: str
    workspace_id: str


class ClientUpdate(BaseModel):
    """Schema for client update"""
    name: Optional[str] = None
    client_metadata: Optional[Dict] = None
