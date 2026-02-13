"""
Health check endpoint schema
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema for health check response."""

    message: str
    version: str
    status: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "User Registration API",
                    "version": "0.1.0",
                    "status": "operational",
                }
            ]
        }
    }
