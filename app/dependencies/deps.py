"""
FastAPI dependencies for dependency injection.
"""

import asyncpg
from fastapi import Depends

from app.db.pool import db_pool
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def get_db_pool() -> asyncpg.Pool:
    """
    Get database connection pool.

    Returns:
        asyncpg.Pool: Database connection pool
    """
    return db_pool.get_pool()


def get_user_repository(pool: asyncpg.Pool = Depends(get_db_pool)) -> UserRepository:
    """
    Get user repository instance.

    Args:
        pool: Database connection pool

    Returns:
        UserRepository: User repository instance
    """
    return UserRepository(pool)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """
    Get user service instance.

    Args:
        user_repository: User repository instance

    Returns:
        UserService: User service instance
    """
    return UserService(user_repository=user_repository)
