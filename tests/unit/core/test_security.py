import pytest
from app.core.security import hash_password, verify_password


@pytest.mark.parametrize(
    "password",
    [
        "simplepass",
        "StrongPass123!",
        "12345678",
        "with spaces",
        "P@ssw0rd🔥",
    ],
)
def test_hash_password_parametrized(password: str):
    hashed = hash_password(password=password)

    # Hash should be a string
    assert isinstance(hashed, str)

    # Hash should not equal raw password
    assert hashed != password

    # Hash should verify correctly
    assert verify_password(plain_password=password, hashed_password=hashed) is True


@pytest.mark.parametrize(
    "plain_password, test_password, expected",
    [
        ("correct_password", "correct_password", True),
        ("correct_password", "wrong_password", False),
        ("123456", "123456", True),
        ("123456", "654321", False),
    ],
)
def test_verify_password_parametrized(plain_password, test_password, expected):
    hashed = hash_password(password=plain_password)
    assert (
        verify_password(plain_password=test_password, hashed_password=hashed)
        is expected
    )
