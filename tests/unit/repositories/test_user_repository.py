import pytest
from unittest.mock import AsyncMock, MagicMock

from app.repositories.user_repository import UserRepository  # adjust if needed


@pytest.mark.asyncio
async def test_create_user_success():
    # Mock row returned from DB
    mock_row = {
        "id": "uuid-123",
        "email": "test@example.com",
        "is_active": False,
        "created_at": "2024-01-01T00:00:00Z",
    }

    # Mock connection
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = mock_row

    # Mock pool.acquire() context manager
    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.create_user("test@example.com", "hashed_password")

    assert result == mock_row
    mock_conn.fetchrow.assert_awaited_once()
