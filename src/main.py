"""
Luxury Ride Share Agent - Main Entry Point
Orchestrates the Claude AI agent with LangChain for ride booking and lead qualification
"""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("DJ Blu Bloods Resources platform starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Claude Model: {settings.CLAUDE_MODEL}")
    yield
    logger.info("DJ Blu Bloods Resources platform shutting down...")


# Create FastAPI application
app = FastAPI(
    title="DJ Blu Bloods Resources",
    description="High-ticket Instagram sales platform for DJ Blu Bloods resources and premium offers",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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


@app.get("/vault", include_in_schema=False)
async def vault_shop_page():
    """Serve the digital vault shop page."""
    return FileResponse(STATIC_DIR / "vault-shop.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "dj-blu-bloods-resources",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
