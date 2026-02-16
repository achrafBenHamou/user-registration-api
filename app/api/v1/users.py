"""
User API endpoints.

This module defines HTTP endpoints related to user registration
and account activation.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.dependencies.deps import get_user_service
from app.exceptions.user import (
    UserAlreadyExistsException,
    UserAlreadyActivatedException,
)
from app.schemas.user import (
    UserCreate,
    UserResponse,
    ActivateUserRequest,
    MessageResponse,
)
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBasic()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. The account will be inactive until activated.",
)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Register a new user account.

    Creates a new user using the provided email and password.
    The created account is inactive until it is verified.

    Args:
        user_data: Payload containing the user's email and password.
        background_tasks: BackgroundTasks dependency.
        user_service: User service Dependency.
    Returns:
        The created user representation with ``is_active`` set to False.

    Raises:
        HTTPException: If the email is already registered or validation fails.
    """
    try:
        user = await user_service.register_user(email=user_data.email, password=user_data.password, background_tasks=background_tasks)
        return UserResponse(**user)
    except UserAlreadyExistsException as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {user_data.email} is already registered",
        )


@router.post(
    "/activation-code",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request activation code",
    description="Generate and send a 4-digit activation code via email. Requires Basic Auth with user credentials.",
)
async def request_activation_code(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """
    Generate and send an activation code to the user.

    Requires HTTP Basic authentication using the user's
    email and password.

    Args:
        credentials: HTTP Basic authentication credentials.
        background_tasks: BackgroundTasks dependency.
        user_service: User service Dependency.

    Returns:
        A confirmation message indicating that the activation
        code has been sent.

    Raises:
        HTTPException: If authentication fails or the user
        account does not exist.
    """
    email = credentials.username
    try:
        await user_service.request_activation_code(
            email=email,
            password=credentials.password,
            background_tasks=background_tasks,
        )
        return MessageResponse(message=f"Activation code sent to your email {email}")
    except UserAlreadyActivatedException as e:
        logger.warning(f"Activation code request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is already activated",
        )


@router.post(
    "/activate",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate user account",
    description="Activate a user account using the 4-digit code received via email. Requires Basic Auth.",
)
async def activate_user(
    activation_data: ActivateUserRequest,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> MessageResponse:
    """
    Activate a user account using a verification code.

    Requires HTTP Basic authentication and a valid 4-digit
    activation code sent to the user's email. The code expires
    after one minute.

    Args:
        activation_data: Request payload containing the activation code.
        credentials: HTTP Basic authentication credentials.

    Returns:
        A confirmation message indicating that the account
        has been successfully activated.

    Raises:
        HTTPException: If authentication fails, the code is invalid,
        or the code has expired.
    """
    raise NotImplementedError("User activation endpoint not implemented yet")
