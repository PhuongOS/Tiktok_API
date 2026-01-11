"""
Auth Service - Main Application
"""
from fastapi import FastAPI
from app.api import auth, workspaces

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Authentication & Authorization Service"
)

# Include routers
app.include_router(auth.router)
app.include_router(workspaces.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "auth-service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

