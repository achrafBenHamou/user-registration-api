"""
Unit tests for MailpitClient.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from app.clients.mailpit_client import MailpitClient


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def mailpit_client(mock_http_client):
    """Create a MailpitClient instance with mocked HTTP client."""
    return MailpitClient(client=mock_http_client)


@pytest.mark.asyncio
async def test_send_email_success(mailpit_client, mock_http_client):
    """Test successful email sending."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_http_client.post = AsyncMock(return_value=mock_response)

    # Act
    result = await mailpit_client.send_email(
        to_email="test@example.com",
        subject="Test Subject",
        text_body="Test body",
    )

    # Assert
    assert result is True
    mock_http_client.post.assert_awaited_once()
    call_args = mock_http_client.post.call_args
    assert call_args.kwargs["json"]["To"][0]["Email"] == "test@example.com"
    assert call_args.kwargs["json"]["Subject"] == "Test Subject"
    assert call_args.kwargs["json"]["Text"] == "Test body"


@pytest.mark.asyncio
async def test_send_email_with_html(mailpit_client, mock_http_client):
    """Test sending email with HTML body."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_http_client.post = AsyncMock(return_value=mock_response)

    # Act
    result = await mailpit_client.send_email(
        to_email="test@example.com",
        subject="Test Subject",
        text_body="Test body",
        html_body="<h1>Test HTML</h1>",
    )

    # Assert
    assert result is True
    call_args = mock_http_client.post.call_args
    assert call_args.kwargs["json"]["HTML"] == "<h1>Test HTML</h1>"


@pytest.mark.asyncio
async def test_send_email_with_custom_from(mailpit_client, mock_http_client):
    """Test sending email with custom from email and name."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_http_client.post = AsyncMock(return_value=mock_response)

    # Act
    result = await mailpit_client.send_email(
        to_email="test@example.com",
        subject="Test Subject",
        text_body="Test body",
        from_email="custom@example.com",
        from_name="Custom Sender",
    )

    # Assert
    assert result is True
    call_args = mock_http_client.post.call_args
    assert call_args.kwargs["json"]["From"]["Email"] == "custom@example.com"
    assert call_args.kwargs["json"]["From"]["Name"] == "Custom Sender"


@pytest.mark.asyncio
async def test_send_email_timeout(mailpit_client, mock_http_client):
    """Test email sending with timeout exception."""
    # Arrange
    mock_http_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

    # Act
    result = await mailpit_client.send_email(
        to_email="test@example.com",
        subject="Test Subject",
        text_body="Test body",
    )

    # Assert
    assert result is False
    mock_http_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_email_connection_error(mailpit_client, mock_http_client):
    """Test email sending with connection error."""
    # Arrange
    mock_http_client.post = AsyncMock(
        side_effect=httpx.ConnectError("Connection failed")
    )

    # Act
    result = await mailpit_client.send_email(
        to_email="test@example.com",
        subject="Test Subject",
        text_body="Test body",
    )

    # Assert
    assert result is False
    mock_http_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_email_http_status_error(mailpit_client, mock_http_client):
    """Test email sending with HTTP status error."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )
    )
    mock_http_client.post = AsyncMock(return_value=mock_response)

    # Act
    result = await mailpit_client.send_email(
        to_email="test@example.com",
        subject="Test Subject",
        text_body="Test body",
    )

    # Assert
    assert result is False
    mock_http_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_email_unexpected_error(mailpit_client, mock_http_client):
    """Test email sending with unexpected error."""
    # Arrange
    mock_http_client.post = AsyncMock(side_effect=Exception("Unexpected error"))

    # Act
    result = await mailpit_client.send_email(
        to_email="test@example.com",
        subject="Test Subject",
        text_body="Test body",
    )

    # Assert
    assert result is False
    mock_http_client.post.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.clients.mailpit_client.settings")
async def test_send_email_uses_settings(mock_settings, mock_http_client):
    """Test that MailpitClient uses settings for defaults."""
    # Arrange
    mock_settings.email_api_url = "http://test-mailpit:8025/api/v1/send"
    mock_settings.email_api_timeout = 15.0
    mock_settings.from_email = "test@example.com"
    mock_settings.from_name = "Test Sender"

    client = MailpitClient(client=mock_http_client)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_http_client.post = AsyncMock(return_value=mock_response)

    # Act
    await client.send_email(
        to_email="recipient@example.com",
        subject="Test",
        text_body="Body",
    )

    # Assert
    call_args = mock_http_client.post.call_args
    assert call_args.args[0] == "http://test-mailpit:8025/api/v1/send"
    assert call_args.kwargs["timeout"] == 15.0
    assert call_args.kwargs["json"]["From"]["Email"] == "test@example.com"
    assert call_args.kwargs["json"]["From"]["Name"] == "Test Sender"
