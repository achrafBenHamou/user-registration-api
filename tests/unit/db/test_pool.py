import pytest
from unittest.mock import AsyncMock, patch

from app.db.pool import DatabasePool


@pytest.mark.asyncio
async def test_connect_creates_pool():
    pool = DatabasePool()

    mock_pool = AsyncMock()

    with patch(
        "app.db.pool.asyncpg.create_pool", new=AsyncMock(return_value=mock_pool)
    ) as mock_create:
        await pool.connect()

        assert pool._pool == mock_pool
        mock_create.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_does_not_recreate_pool_if_exists():
    pool = DatabasePool()
    pool._pool = AsyncMock()

    with patch("app.db.pool.asyncpg.create_pool", new=AsyncMock()) as mock_create:
        await pool.connect()

        mock_create.assert_not_called()


@pytest.mark.asyncio
async def test_close_closes_pool():
    pool = DatabasePool()
    mock_pool = AsyncMock()
    pool._pool = mock_pool

    await pool.close()

    mock_pool.close.assert_awaited_once()
    assert pool._pool is None


@pytest.mark.asyncio
async def test_close_when_pool_is_none():
    pool = DatabasePool()

    # Should not raise
    await pool.close()

    assert pool._pool is None


def test_get_pool_raises_if_not_initialized():
    pool = DatabasePool()

    with pytest.raises(RuntimeError, match="Database pool not initialized"):
        pool.get_pool()


def test_get_pool_returns_pool():
    pool = DatabasePool()
    mock_pool = AsyncMock()
    pool._pool = mock_pool

    assert pool.get_pool() == mock_pool
