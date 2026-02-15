"""
Security utilities for password hashing and verification.
"""

import bcrypt

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Another cryptographic hashing algorithm could be used here,
    but bcrypt is a widely adopted for password hashing.
    Args:
        password: Plain text password

    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
