"""
User service containing business logic.
"""

import logging
from asyncpg.exceptions import UniqueViolationError

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password
from app.exceptions.user import UserAlreadyExistsException

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related business logic."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, email: str, password: str) -> dict:
        """
        Register a new user.

        Args:
            email: User email
            password: Plain text password

        Returns:
            dict: Created user data

        Raises:
            UserAlreadyExistsException: If email already exists
        """
        try:
            # Hash password
            hashed_password = hash_password(password=password)

            # Create user
            user = await self.user_repository.create_user(
                email=email, hashed_password=hashed_password
            )

            logger.info(f"User registered: {email}")
            return user

        except UniqueViolationError:
            logger.warning(f"Registration failed: email {email} already exists")
            raise UserAlreadyExistsException(email=email)
