"""
Security utilities for password hashing and verification.
"""


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password as string
    """
    raise NotImplementedError("hash_password function is not implemented yet")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    raise NotImplementedError("verify_password function is not implemented yet")
