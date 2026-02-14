"""
API v1 router configuration.
"""

from fastapi import APIRouter

from app.api.v1 import users

router = APIRouter()

# Include user endpoints
router.include_router(users.router, prefix="/users", tags=["users"])
