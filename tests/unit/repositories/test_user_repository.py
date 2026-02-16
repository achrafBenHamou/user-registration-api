import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from app.repositories.user_repository import UserRepository

# -------------------------
# CREATE USER
# -------------------------


@pytest.mark.asyncio
async def test_create_user_success():
    mock_row = {
        "id": "uuid-123",
        "email": "test@example.com",
        "is_active": False,
        "created_at": "2024-01-01T00:00:00Z",
    }

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = mock_row

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.create_user("test@example.com", "hashed_password")

    assert result == mock_row
    mock_conn.fetchrow.assert_awaited_once()


# -------------------------
# GET USER BY EMAIL
# -------------------------


@pytest.mark.asyncio
async def test_get_user_by_email_found():
    mock_row = {
        "id": "uuid-123",
        "email": "test@example.com",
        "hashed_password": "hashed",
        "is_active": False,
        "created_at": datetime.utcnow(),
    }

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = mock_row

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.get_user_by_email("test@example.com")

    assert result == mock_row


@pytest.mark.asyncio
async def test_get_user_by_email_not_found():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.get_user_by_email("missing@example.com")

    assert result is None


# -------------------------
# CREATE ACTIVATION CODE
# -------------------------


@pytest.mark.asyncio
@patch("app.repositories.user_repository.settings")
@patch("app.repositories.user_repository.secrets.randbelow")
async def test_create_activation_code_success(mock_randbelow, mock_settings):
    user_id = uuid4()

    mock_randbelow.return_value = 1234
    mock_settings.activation_code_ttl_seconds = 60

    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()

    # Proper transaction mock
    mock_transaction = MagicMock()
    mock_transaction.__aenter__ = AsyncMock(return_value=None)
    mock_transaction.__aexit__ = AsyncMock(return_value=None)
    mock_conn.transaction.return_value = mock_transaction

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    code = await repo.create_activation_code(user_id)

    assert code == "2234"


# -------------------------
# VERIFY ACTIVATION CODE
# -------------------------


@pytest.mark.asyncio
async def test_verify_activation_code_valid():
    user_id = uuid4()

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 1}

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.verify_activation_code(user_id, "1234")

    assert result is True


@pytest.mark.asyncio
async def test_verify_activation_code_invalid():
    user_id = uuid4()

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.verify_activation_code(user_id, "9999")

    assert result is False


# -------------------------
# DELETE ACTIVATION CODE
# -------------------------


@pytest.mark.asyncio
async def test_delete_activation_code():
    user_id = uuid4()

    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    await repo.delete_activation_code(user_id)

    mock_conn.execute.assert_awaited_once()


# -------------------------
# HAS ACTIVATION CODE
# -------------------------


@pytest.mark.asyncio
async def test_has_activation_code_true():
    user_id = uuid4()

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 1}

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.has_activation_code(user_id)

    assert result is True


@pytest.mark.asyncio
async def test_has_activation_code_false():
    user_id = uuid4()

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.has_activation_code(user_id)

    assert result is False


# -------------------------
# ACTIVATE USER
# -------------------------


@pytest.mark.asyncio
async def test_activate_user_success():
    user_id = uuid4()

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": user_id}

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.activate_user(user_id)

    assert result is True


@pytest.mark.asyncio
async def test_activate_user_not_updated():
    user_id = uuid4()

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = AsyncMock()

    repo = UserRepository(pool=mock_pool)

    result = await repo.activate_user(user_id)

    assert result is False
