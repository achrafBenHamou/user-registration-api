"""
User repository for database operations.
"""

import asyncpg


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_user(self, email: str, hashed_password: str) -> dict:
        """
        Create a new user in the database.

        Args:
            email: User email
            hashed_password: Hashed password

        Returns:
            dict: Created user data

        Raises:
            asyncpg.UniqueViolationError: If email already exists
        """
        query = """
            INSERT INTO users (email, hashed_password, is_active)
            VALUES ($1, $2, FALSE)
            RETURNING id, email, is_active, created_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, email, hashed_password)
            return dict(row)
