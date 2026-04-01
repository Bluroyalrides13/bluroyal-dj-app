"""
Luxury Ride Share Agent - Main Entry Point
Orchestrates the Claude AI agent with LangChain for ride booking and lead qualification
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from src.api.routes import router
from src.api.websocket import setup_websocket
from config.settings import Settings

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load settings
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("🚗 Luxury Ride Share Agent starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Claude Model: {settings.CLAUDE_MODEL}")
    yield
    logger.info("🛑 Luxury Ride Share Agent shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Luxury Ride Share Agent",
    description="AI-powered lead qualification and booking management for luxury ride share",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Wix integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Setup WebSocket for real-time chat
setup_websocket(app)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "luxury-rideshare-agent",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
