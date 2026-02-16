"""
User service containing business logic.
"""

import logging
from asyncpg.exceptions import UniqueViolationError
from fastapi import BackgroundTasks

from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.exceptions.user import (
    UserAlreadyExistsException,
    UserAlreadyActivatedException,
    InvalidCredentialsException,
)
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related business logic."""

    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service

    async def register_user(
        self, email: str, password: str, background_tasks: BackgroundTasks
    ) -> dict:
        """
        Register a new user.

        Args:
            email: User email
            password: Plain text password
            background_tasks: Background tasks

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
            if settings.send_activation_code_on_registration:
                logger.info(
                    f"Sending activation code to {email} since send_activation_code_on_registration is True"
                )
                await self.request_activation_code(
                    email=email, password=password, background_tasks=background_tasks
                )
            logger.info(f"User registered: {email}")
            return user

        except UniqueViolationError:
            logger.warning(f"Registration failed: email {email} already exists")
            raise UserAlreadyExistsException(email=email)

    async def authenticate_user(self, email: str, password: str) -> dict:
        """
        Authenticate a user with email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            dict: User data if authentication successful

        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        user = await self.user_repository.get_user_by_email(email)

        if not user:
            logger.warning(f"Authentication failed: user {email} not found")
            raise InvalidCredentialsException()

        if not verify_password(password, user["hashed_password"]):
            logger.warning(f"Authentication failed: invalid password for {email}")
            raise InvalidCredentialsException()

        logger.info(f"User authenticated: {email}")
        return user

    async def request_activation_code(
        self, email: str, password: str, background_tasks: BackgroundTasks
    ) -> None:
        """
        Generate and send activation code to user.

        Args:
            email: User email
            password: Plain text password
            background_tasks: Background tasks

        Raises:
            InvalidCredentialsException: If credentials are invalid
            UserAlreadyActivatedException: If user is already activated
        """
        # Authenticate user
        user = await self.authenticate_user(email=email, password=password)

        # Check if already activated
        if user["is_active"]:
            logger.warning(
                f"Activation code request failed: user {email} already activated"
            )
            raise UserAlreadyActivatedException()

        # Generate activation code
        code = await self.user_repository.create_activation_code(user["id"])

        # Send email with code
        # No need to await here since, user could request a new code if email fails, and we don't want to block the response
        # Fails  are logged in the email service, and user can request a new code if they don't receive it, so we don't need to handle failures here
        background_tasks.add_task(
            self.email_service.send_activation_code,
            to_email=email,
            code=code,
        )