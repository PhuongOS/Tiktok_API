"""
Device Service API
"""
from app.api.devices import router as devices_router
from app.api.websocket import router as websocket_router
from app.api.webhook import router as webhook_router

__all__ = [
    "devices_router",
    "websocket_router",
    "webhook_router",
]
