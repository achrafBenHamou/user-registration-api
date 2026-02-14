"""
Pydantic schemas for user-related operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password must be between 8 and 100 characters",
    )


class UserResponse(BaseModel):
    """Schema for user response."""

    id: UUID
    email: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivationCodeRequest(BaseModel):
    """Schema for activation code request."""

    pass  # Body is empty, uses Basic Auth for user identification


class ActivateUserRequest(BaseModel):
    """Schema for user activation."""

    code: str = Field(
        ...,
        min_length=4,
        max_length=4,
        pattern=r"^\d{4}$",
        description="4-digit numeric activation code",
    )


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class ErrorResponse(BaseModel):
    """Error response schema."""

    code_error: str
    detail: str
