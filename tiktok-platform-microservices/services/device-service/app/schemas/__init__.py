"""
Device Service Schemas
"""
from app.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceWithToken,
    CommandCreate,
    CommandResponse,
)

__all__ = [
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    "DeviceWithToken",
    "CommandCreate",
    "CommandResponse",
]
