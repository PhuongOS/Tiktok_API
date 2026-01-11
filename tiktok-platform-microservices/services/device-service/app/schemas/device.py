"""
Pydantic schemas for Device Service
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.device import DeviceType, DeviceStatus, CommandStatus


# ============= Device Schemas =============

class DeviceCreate(BaseModel):
    """Schema for creating a device"""
    name: str = Field(..., min_length=1, max_length=100, description="Device name")
    device_type: DeviceType = Field(..., description="Device type")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Custom device properties")


class DeviceUpdate(BaseModel):
    """Schema for updating a device"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Device name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom device properties")


class DeviceResponse(BaseModel):
    """Schema for device response"""
    id: str
    workspace_id: str
    name: str
    device_type: DeviceType
    status: DeviceStatus
    last_seen: Optional[datetime] = None
    device_metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DeviceWithToken(DeviceResponse):
    """Schema for device response with token (only returned on creation)"""
    token: str = Field(..., description="Authentication token for device (save this!)")


# ============= Command Schemas =============

class CommandCreate(BaseModel):
    """Schema for creating a command"""
    command_type: str = Field(..., description="Command type (turn_on, turn_off, set_brightness, custom)")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Command parameters")


class CommandResponse(BaseModel):
    """Schema for command response"""
    id: str
    device_id: str
    command_type: str
    parameters: Dict[str, Any] = {}
    status: CommandStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= Webhook Schemas =============

class WebhookControlRequest(BaseModel):
    """Schema for webhook control request from Rule Engine"""
    workspace_id: str = Field(..., description="Workspace ID")
    device_id: str = Field(..., description="Device ID")
    command_type: str = Field(..., description="Command type")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Command parameters")


class WebhookControlResponse(BaseModel):
    """Schema for webhook control response"""
    command_id: str = Field(..., description="Command ID for tracking")
    status: str = Field(..., description="Command status")
    message: str = Field(..., description="Response message")
