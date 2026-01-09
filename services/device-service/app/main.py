"""
Device Service - FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Device Service",
    description="IoT Device Management and Control Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for debugging"""
    logger.error(f"Global exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )

# Import routers
from app.api.devices import router as devices_router
from app.api.websocket import router as websocket_router
from app.api.webhook import router as webhook_router

# Include routers
app.include_router(devices_router)
app.include_router(websocket_router)
app.include_router(webhook_router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Device Service starting up...")
    logger.info("WebSocket manager initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Device Service shutting down...")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.services.websocket_manager import websocket_manager
    
    return {
        "status": "healthy",
        "service": "device-service",
        "version": "0.1.0",
        "active_connections": websocket_manager.get_connection_count(),
        "connected_devices": websocket_manager.get_connected_devices()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Device Service",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }
