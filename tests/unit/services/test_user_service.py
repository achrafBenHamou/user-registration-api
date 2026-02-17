import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from asyncpg.exceptions import UniqueViolationError
from fastapi import BackgroundTasks

from app.services.user_service import UserService
from app.exceptions.user import (
    UserAlreadyExistsException,
    UserAlreadyActivatedException,
    InvalidCredentialsException,
    NoActivationCodeException,
    InvalidActivationCodeException,
)

# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture
def mock_user_repository():
    return AsyncMock()


@pytest.fixture
def mock_email_service():
    return AsyncMock()


@pytest.fixture
def user_service(mock_user_repository, mock_email_service):
    return UserService(
        user_repository=mock_user_repository,
        email_service=mock_email_service,
    )


@pytest.fixture
def background_tasks():
    return MagicMock(spec=BackgroundTasks)


# ==========================================================
# register_user
# ==========================================================


@pytest.mark.asyncio
@patch("app.services.user_service.hash_password", return_value="hashed_pw")
@patch("app.services.user_service.settings")
async def test_register_user_success_without_activation(
    mock_settings,
    mock_hash,
    user_service,
    mock_user_repository,
    background_tasks,
):
    mock_settings.send_activation_code_on_registration = False

    mock_user_repository.create_user.return_value = {
        "id": 1,
        "email": "test@example.com",
    }

    result = await user_service.register_user(
        "test@example.com",
        "password",
        background_tasks,
    )

    assert result["email"] == "test@example.com"
    mock_user_repository.create_user.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.services.user_service.hash_password", return_value="hashed_pw")
@patch("app.services.user_service.settings")
async def test_register_user_success_with_activation(
    mock_settings,
    mock_hash,
    user_service,
    mock_user_repository,
    background_tasks,
):
    mock_settings.send_activation_code_on_registration = True

    mock_user_repository.create_user.return_value = {
        "id": 1,
        "email": "test@example.com",
    }

    result = await user_service.register_user(
        "test@example.com",
        "password",
        background_tasks,
    )

    assert result["email"] == "test@example.com"
    background_tasks.add_task.assert_called_once_with(
        user_service._generate_and_send_activation_code,
        user_id=1,
        email="test@example.com",
    )


@pytest.mark.asyncio
@patch("app.services.user_service.hash_password", return_value="hashed_pw")
async def test_register_user_duplicate_email(
    mock_hash,
    user_service,
    mock_user_repository,
    background_tasks,
):
    mock_user_repository.create_user.side_effect = UniqueViolationError(
        "error",
        "detail",
    )

    with pytest.raises(UserAlreadyExistsException):
        await user_service.register_user(
            "test@example.com",
            "password",
            background_tasks,
        )


# ==========================================================
# authenticate_user
# ==========================================================


@pytest.mark.asyncio
@patch("app.services.user_service.verify_password", return_value=True)
async def test_authenticate_user_success(
    mock_verify,
    user_service,
    mock_user_repository,
):
    mock_user_repository.get_user_by_email.return_value = {
        "id": 1,
        "email": "test@example.com",
        "hashed_password": "hashed_pw",
    }

    user = await user_service.authenticate_user(
        "test@example.com",
        "password",
    )

    assert user["id"] == 1


@pytest.mark.asyncio
async def test_authenticate_user_not_found(
    user_service,
    mock_user_repository,
):
    mock_user_repository.get_user_by_email.return_value = None

    with pytest.raises(InvalidCredentialsException):
        await user_service.authenticate_user(
            "test@example.com",
            "password",
        )


@pytest.mark.asyncio
@patch("app.services.user_service.verify_password", return_value=False)
async def test_authenticate_user_invalid_password(
    mock_verify,
    user_service,
    mock_user_repository,
):
    mock_user_repository.get_user_by_email.return_value = {
        "id": 1,
        "email": "test@example.com",
        "hashed_password": "hashed_pw",
    }

    with pytest.raises(InvalidCredentialsException):
        await user_service.authenticate_user(
            "test@example.com",
            "wrong_password",
        )


# ==========================================================
# request_activation_code
# ==========================================================


@pytest.mark.asyncio
async def test_generate_and_send_activation_code_success(
    user_service,
    mock_user_repository,
    mock_email_service,
):
    mock_user_repository.create_activation_code.return_value = "1234"

    await user_service._generate_and_send_activation_code(
        user_id=1,
        email="test@example.com",
    )

    mock_user_repository.create_activation_code.assert_awaited_once_with(1)
    mock_email_service.send_activation_code.assert_awaited_once_with(
        to_email="test@example.com",
        code="1234",
    )


@pytest.mark.asyncio
async def test_generate_and_send_activation_code_failure_in_generation(
    user_service,
    mock_user_repository,
    mock_email_service,
):
    mock_user_repository.create_activation_code.side_effect = Exception(
        "Database error"
    )

    # Should not raise, errors are logged
    await user_service._generate_and_send_activation_code(
        user_id=1,
        email="test@example.com",
    )

    mock_user_repository.create_activation_code.assert_awaited_once_with(1)
    mock_email_service.send_activation_code.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_and_send_activation_code_failure_in_sending(
    user_service,
    mock_user_repository,
    mock_email_service,
):
    mock_user_repository.create_activation_code.return_value = "1234"
    mock_email_service.send_activation_code.side_effect = Exception("Email error")

    # Should not raise, errors are logged
    await user_service._generate_and_send_activation_code(
        user_id=1,
        email="test@example.com",
    )

    mock_user_repository.create_activation_code.assert_awaited_once_with(1)
    mock_email_service.send_activation_code.assert_awaited_once()


# ==========================================================
# request_activation_code
# ==========================================================


@pytest.mark.asyncio
async def test_request_activation_code_success(
    user_service,
    mock_user_repository,
    background_tasks,
):
    user_service.authenticate_user = AsyncMock(
        return_value={"id": 1, "is_active": False}
    )

    await user_service.request_activation_code(
        "test@example.com",
        "password",
        background_tasks,
    )

    background_tasks.add_task.assert_called_once_with(
        user_service._generate_and_send_activation_code,
        user_id=1,
        email="test@example.com",
    )


@pytest.mark.asyncio
async def test_request_activation_code_user_already_active(
    user_service,
    background_tasks,
):
    user_service.authenticate_user = AsyncMock(
        return_value={"id": 1, "is_active": True}
    )

    with pytest.raises(UserAlreadyActivatedException):
        await user_service.request_activation_code(
            "test@example.com",
            "password",
            background_tasks,
        )


@pytest.mark.asyncio
async def test_request_activation_code_invalid_credentials(
    user_service,
    background_tasks,
):
    user_service.authenticate_user = AsyncMock(
        side_effect=InvalidCredentialsException()
    )

    with pytest.raises(InvalidCredentialsException):
        await user_service.request_activation_code(
            "test@example.com",
            "password",
            background_tasks,
        )


# ==========================================================
# activate_user
# ==========================================================


@pytest.mark.asyncio
async def test_activate_user_success(
    user_service,
    mock_user_repository,
):
    user_service.authenticate_user = AsyncMock(
        return_value={"id": 1, "is_active": False}
    )

    mock_user_repository.has_activation_code.return_value = True
    mock_user_repository.verify_activation_code.return_value = True

    await user_service.activate_user(
        "test@example.com",
        "password",
        "1234",
    )

    mock_user_repository.activate_user.assert_awaited_once_with(1)
    mock_user_repository.delete_activation_code.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_activate_user_already_active(user_service):
    user_service.authenticate_user = AsyncMock(
        return_value={"id": 1, "is_active": True}
    )

    with pytest.raises(UserAlreadyActivatedException):
        await user_service.activate_user(
            "test@example.com",
            "password",
            "1234",
        )


@pytest.mark.asyncio
async def test_activate_user_no_activation_code(
    user_service,
    mock_user_repository,
):
    user_service.authenticate_user = AsyncMock(
        return_value={"id": 1, "is_active": False}
    )

    mock_user_repository.has_activation_code.return_value = False

    with pytest.raises(NoActivationCodeException):
        await user_service.activate_user(
            "test@example.com",
            "password",
            "1234",
        )


@pytest.mark.asyncio
async def test_activate_user_invalid_code(
    user_service,
    mock_user_repository,
):
    user_service.authenticate_user = AsyncMock(
        return_value={"id": 1, "is_active": False}
    )

    mock_user_repository.has_activation_code.return_value = True
    mock_user_repository.verify_activation_code.return_value = False

    with pytest.raises(InvalidActivationCodeException):
        await user_service.activate_user(
            "test@example.com",
            "password",
            "wrong_code",
        )


@pytest.mark.asyncio
async def test_activate_user_invalid_credentials(user_service):
    user_service.authenticate_user = AsyncMock(
        side_effect=InvalidCredentialsException()
    )

    with pytest.raises(InvalidCredentialsException):
        await user_service.activate_user(
            "test@example.com",
            "password",
            "1234",
        )
