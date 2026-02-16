"""
Test configuration and fixtures.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.pool import db_pool


@pytest_asyncio.fixture(scope="function")
async def setup_database() -> AsyncGenerator:
    """
    Setup database connection pool for testing.
    Reconnects for each test to avoid event loop issues.
    """
    # Ensure pool is closed first
    try:
        await db_pool.close()
    except:
        pass

    # Connect to database
    await db_pool.connect()
    yield

    # Cleanup and close
    await db_pool.close()


@pytest_asyncio.fixture
async def clean_database(setup_database):
    """
    Clean up database before each test.
    Removes all test data to ensure test isolation.
    """
    # Clean up before test
    async with db_pool.get_pool().acquire() as conn:
        await conn.execute("DELETE FROM activation_codes")
        await conn.execute("DELETE FROM users")

    yield

    # Clean up after test
    async with db_pool.get_pool().acquire() as conn:
        await conn.execute("DELETE FROM activation_codes")
        await conn.execute("DELETE FROM users")


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
