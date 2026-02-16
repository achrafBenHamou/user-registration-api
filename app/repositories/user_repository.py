"""
User repository for database operations.
"""

from typing import Optional

import asyncpg
import secrets

from datetime import datetime, timedelta
from uuid import UUID
from app.core.config import settings


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

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            dict or None: User data if found, None otherwise
        """
        query = """
            SELECT id, email, hashed_password, is_active, created_at
            FROM users
            WHERE email = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, email)
            return dict(row) if row else None

    async def create_activation_code(self, user_id: UUID) -> str:
        """
        Create an activation code for a user.
        Deletes any existing codes for this user first.

        Args:
            user_id: User UUID

        Returns:
            str: The generated 4-digit code
        """
        # Generate 4-digit code
        code = f"{secrets.randbelow(9000) + 1000}"

        # Calculate expiration time (1 minute from now)
        expires_at = datetime.utcnow() + timedelta(
            seconds=settings.activation_code_ttl_seconds
        )

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Delete existing codes for this user
                await conn.execute(
                    "DELETE FROM activation_codes WHERE user_id = $1", user_id
                )

                # Insert new code
                await conn.execute(
                    """
                    INSERT INTO activation_codes (user_id, code, expires_at)
                    VALUES ($1, $2, $3)
                    """,
                    user_id,
                    code,
                    expires_at,
                )

        return code

    async def verify_activation_code(self, user_id: UUID, code: str) -> bool:
        """
        Verify an activation code for a user.

        Args:
            user_id: User UUID
            code: 4-digit activation code

        Returns:
            bool: True if code is valid and not expired, False otherwise
        """
        query = """
            SELECT id
            FROM activation_codes
            WHERE user_id = $1 
            AND code = $2 
            AND expires_at > NOW()
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, code)
            return row is not None

    async def delete_activation_code(self, user_id: UUID) -> None:
        """
        Delete activation code(s) for a user.

        Args:
            user_id: User UUID
        """
        query = "DELETE FROM activation_codes WHERE user_id = $1"
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id)

    async def has_activation_code(self, user_id: UUID) -> bool:
        """
        Check if user has an activation code.

        Args:
            user_id: User UUID

        Returns:
            bool: True if user has an activation code, False otherwise
        """
        query = """
            SELECT id
            FROM activation_codes
            WHERE user_id = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
            return row is not None

