"""
Rule Engine Service - FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.rules import router as rules_router
from app.services.event_consumer import event_consumer
import asyncio
import traceback

app = FastAPI(
    title="Rule Engine Service",
    description="Event-driven automation rule engine",
    version="1.0.0"
)

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "trace": traceback.format_exc()},
    )

# Lifecycle Events
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    print("🚀 App Startup: Starting Consumer...")
    asyncio.create_task(event_consumer.start())

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks"""
    print("🛑 App Shutdown: Stopping Consumer...")
    await event_consumer.stop()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rules_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Rule Engine Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
