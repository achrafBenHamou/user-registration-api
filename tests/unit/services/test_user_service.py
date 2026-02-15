import pytest

from unittest.mock import patch, AsyncMock

from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_register_user_success():
    mock_repo = AsyncMock()
    mock_repo.create_user.return_value = {
        "id": "uuid-123",
        "email": "test@example.com",
        "is_active": False,
    }

    service = UserService(user_repository=mock_repo)

    with patch("app.services.user_service.hash_password") as mock_hash:
        mock_hash.return_value = "hashed_password"

        result = await service.register_user(
            email="test@example.com", password="plain_password"
        )

        # Ensure hashing was called
        mock_hash.assert_called_once_with(password="plain_password")

        # Ensure repository was called with hashed password
        mock_repo.create_user.assert_awaited_once_with(
            email="test@example.com",
            hashed_password="hashed_password",
        )

        assert result["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_user_success():
    mock_repo = AsyncMock()
    mock_repo.create_user.return_value = {
        "id": "uuid-123",
        "email": "test@example.com",
        "is_active": False,
    }

    service = UserService(user_repository=mock_repo)

    with patch("app.services.user_service.hash_password") as mock_hash:
        mock_hash.return_value = "hashed_password"

        result = await service.register_user(
            email="test@example.com", password="plain_password"
        )

        # Ensure hashing was called
        mock_hash.assert_called_once_with(password="plain_password")

        # Ensure repository was called with hashed password
        mock_repo.create_user.assert_awaited_once_with(
            email="test@example.com",
            hashed_password="hashed_password",
        )

        assert result["email"] == "test@example.com"
