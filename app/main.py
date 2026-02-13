"""
User Registration API with email activation code (1-minute TTL)
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown events.
    """
    logger.info("Starting lifespan mode")
    yield
    logger.info("Finished lifespan mode")


app = FastAPI(
    title="User Registration API",
    description="User Registration API with email activation code (1-minute TTL)",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify allowed origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Specify allowed HTTP methods
    allow_headers=["*"],  # Specify allowed headers
)


@app.get("/", tags=["health"], response_model=HealthResponse)
@app.get("/health", tags=["health"], response_model=HealthResponse)
async def root():
    """
    Endpoint to verify API is running
    """
    return {
        "message": "User Registration API",
        "version": "0.1.0",
        "status": "operational",
    }
