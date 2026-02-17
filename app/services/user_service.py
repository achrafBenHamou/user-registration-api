"""
User service containing business logic.
"""

import logging
from uuid import UUID

from asyncpg.exceptions import UniqueViolationError
from fastapi import BackgroundTasks

from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.exceptions.user import (
    UserAlreadyExistsException,
    UserAlreadyActivatedException,
    InvalidCredentialsException,
    NoActivationCodeException,
    InvalidActivationCodeException,
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

            # Schedule activation code generation and sending in background (non-blocking)
            if settings.send_activation_code_on_registration:
                logger.info(f"Scheduling activation code to be sent to {email}")
                background_tasks.add_task(
                    self._generate_and_send_activation_code,
                    user_id=user["id"],
                    email=email,
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

    async def _generate_and_send_activation_code(
        self, user_id: UUID, email: str
    ) -> None:
        """
        Generate activation code and send it via email (background task).
        Errors are logged but don't block the user registration flow.

        Args:
            user_id: User ID
            email: User email
        """
        try:
            # Generate activation code
            code = await self.user_repository.create_activation_code(user_id)
            logger.info(f"Activation code generated for user {email}")

            # Send email with code
            await self.email_service.send_activation_code(
                to_email=email,
                code=code,
            )
            logger.info(f"Activation code sent to {email}")

        except Exception as e:
            logger.error(
                f"Failed to generate or send activation code for {email}: {e}",
                exc_info=True,
            )

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

        # Schedule code generation and sending in background (non-blocking)
        background_tasks.add_task(
            self._generate_and_send_activation_code,
            user_id=user["id"],
            email=email,
        )

    async def activate_user(self, email: str, password: str, code: str) -> None:
        """
        Activate a user account with the provided code.

        Args:
            email: User email
            password: Plain text password
            code: 4-digit activation code

        Raises:
            InvalidCredentialsException: If credentials are invalid
            UserAlreadyActivatedException: If user is already activated
            NoActivationCodeException: If no activation code exists
            InvalidActivationCodeException: If code is invalid or expired
        """
        # Authenticate user
        user = await self.authenticate_user(email=email, password=password)

        # Check if already activated
        if user["is_active"]:
            logger.warning(f"Activation failed: user {email} already activated")
            raise UserAlreadyActivatedException()

        # Check if activation code exists
        has_code = await self.user_repository.has_activation_code(user["id"])
        if not has_code:
            logger.warning(f"Activation failed: no code for user {email}")
            raise NoActivationCodeException()

        # Verify activation code
        is_valid = await self.user_repository.verify_activation_code(user["id"], code)

        if not is_valid:
            logger.warning(f"Activation failed: invalid or expired code for {email}")
            raise InvalidActivationCodeException()

        # Activate user
        await self.user_repository.activate_user(user["id"])

        # Delete activation code
        await self.user_repository.delete_activation_code(user["id"])

        logger.info(f"User activated: {email}")
