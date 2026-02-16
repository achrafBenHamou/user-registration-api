"""
User-related exception classes.
"""

from fastapi import status
from app.exceptions.base import AppException


class UserAlreadyExistsException(AppException):
    """Raised when attempting to create a user with an email that already exists."""

    def __init__(self, email: str):
        super().__init__(
            message=f"User with email {email} already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidCredentialsException(AppException):
    """Raised when authentication credentials are invalid."""

    def __init__(self):
        super().__init__(
            message="Invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED
        )


class UserAlreadyActivatedException(AppException):
    """Raised when attempting to activate an already active user."""

    def __init__(self):
        super().__init__(
            message="User account is already activated",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
