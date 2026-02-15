"""
Database connection pool management using asyncpg.
"""

import asyncpg
from typing import Optional

from app.core.config import settings


class DatabasePool:
    """Database connection pool manager."""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create database connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=settings.database_url,
                min_size=settings.database_pool_min_size,
                max_size=settings.database_pool_max_size,
                timeout=settings.database_pool_timeout,
                command_timeout=settings.database_command_timeout,
            )

    async def close(self):
        """Close database connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def get_pool(self) -> asyncpg.Pool:
        """Get the connection pool.

        Returns:
            asyncpg.Pool: Database connection pool

        Raises:
            RuntimeError: If pool is not initialized
        """
        if self._pool is None:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        return self._pool


# Global database pool instance
db_pool = DatabasePool()
