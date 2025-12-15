"""
Main application entry point.
Production-grade FastAPI application with WebSocket support.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.websocket import websocket_endpoint
from app.api.routes import router
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown logic.
    """
    # Startup
    logger.info("Starting Conversational AI Backend...")
    logger.info(f"Server will run on {settings.host}:{settings.port}")
    yield
    # Shutdown
    logger.info("Shutting down Conversational AI Backend...")


# Create FastAPI application
app = FastAPI(
    title="Conversational AI Backend",
    description="Production-grade real-time conversational AI with WebSocket streaming and LLM orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routes
app.include_router(router, prefix="/api", tags=["api"])

# WebSocket endpoint
app.add_api_websocket_route(
    "/ws/session/{session_id}",
    websocket_endpoint,
    name="websocket_session"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Conversational AI Backend",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/ws/session/{session_id}",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level="info",
        reload=True
    )

