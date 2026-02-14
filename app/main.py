"""
User Registration API with email activation code (1-minute TTL)
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.schemas.health import HealthResponse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

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
    title=settings.app_description,
    description="User Registration API with email activation code (1-minute TTL)",
    version=settings.app_version,
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


# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["health"], response_model=HealthResponse)
@app.get("/health", tags=["health"], response_model=HealthResponse)
async def root():
    """
    Endpoint to verify API is running
    """
    return {
        "message": settings.app_description,
        "version": settings.app_version,
        "status": "operational",
    }
