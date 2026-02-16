import pytest
from unittest.mock import AsyncMock

from app.services.email_service import EmailService
from app.clients.mailpit_client import MailpitClient


@pytest.fixture
def mock_mailpit_client():
    """Create a mock MailpitClient for testing."""
    return AsyncMock(spec=MailpitClient)


@pytest.fixture
def email_service(mock_mailpit_client):
    """Create an EmailService instance with mocked MailpitClient."""
    return EmailService(mailpit_client=mock_mailpit_client)


@pytest.mark.asyncio
async def test_send_activation_code_success(email_service, mock_mailpit_client):
    """Test successful activation code email sending."""
    # Arrange
    mock_mailpit_client.send_email = AsyncMock(return_value=True)

    # Act
    result = await email_service.send_activation_code("test@example.com", "1234")

    # Assert
    assert result is True
    mock_mailpit_client.send_email.assert_awaited_once()
    call_args = mock_mailpit_client.send_email.call_args
    assert call_args.kwargs["to_email"] == "test@example.com"
    assert call_args.kwargs["subject"] == "Your Activation Code"
    assert "1234" in call_args.kwargs["text_body"]
    assert "1234" in call_args.kwargs["html_body"]


@pytest.mark.asyncio
async def test_send_activation_code_failure(email_service, mock_mailpit_client):
    """Test failed activation code email sending."""
    # Arrange
    mock_mailpit_client.send_email = AsyncMock(return_value=False)

    # Act
    result = await email_service.send_activation_code("test@example.com", "1234")

    # Assert
    assert result is False
    mock_mailpit_client.send_email.assert_awaited_once()


def test_build_text_body():
    """Test text body generation."""
    ttl = 5
    code = "1234"

    body = EmailService._build_text_body(ttl, code)

    assert "1234" in body
    assert "5" in body
    assert "expires" in body


def test_build_html_body():
    """Test HTML body generation."""
    ttl = 5
    code = "1234"

    body = EmailService._build_html_body(ttl, code)

    assert "1234" in body
    assert "<h2>" in body
    assert "5" in body
