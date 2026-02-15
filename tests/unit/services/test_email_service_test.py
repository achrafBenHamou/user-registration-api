import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.email_service import EmailService


@pytest.fixture
def email_service():
    # We pass a dummy client since your implementation creates a new AsyncClient internally
    return EmailService(client=AsyncMock())


@pytest.mark.asyncio
@patch("app.services.email_service.httpx.AsyncClient")
async def test_send_activation_code_success(mock_async_client, email_service):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    # Mock async context manager
    mock_async_client.return_value.__aenter__.return_value = mock_client_instance

    # Act
    await email_service.send_activation_code("test@example.com", "1234")

    # Assert
    mock_client_instance.post.assert_awaited_once()
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.email_service.httpx.AsyncClient")
async def test_send_activation_code_timeout(mock_async_client, email_service):
    # Arrange
    mock_client_instance = AsyncMock()
    mock_client_instance.post.side_effect = httpx.TimeoutException("Timeout")

    mock_async_client.return_value.__aenter__.return_value = mock_client_instance

    # Act (should not raise)
    await email_service.send_activation_code("test@example.com", "1234")

    # Assert
    mock_client_instance.post.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.services.email_service.httpx.AsyncClient")
async def test_send_activation_code_connection_error(mock_async_client, email_service):
    # Arrange
    mock_client_instance = AsyncMock()
    mock_client_instance.post.side_effect = httpx.ConnectError("Connection failed")

    mock_async_client.return_value.__aenter__.return_value = mock_client_instance

    # Act (should not raise)
    await email_service.send_activation_code("test@example.com", "1234")

    # Assert
    mock_client_instance.post.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.services.email_service.httpx.AsyncClient")
async def test_send_activation_code_unexpected_error(mock_async_client, email_service):
    # Arrange
    mock_client_instance = AsyncMock()
    mock_client_instance.post.side_effect = Exception("Unexpected error")

    mock_async_client.return_value.__aenter__.return_value = mock_client_instance

    # Act (should not raise)
    await email_service.send_activation_code("test@example.com", "1234")

    # Assert
    mock_client_instance.post.assert_awaited_once()


def test_build_text_body():
    ttl = 5
    code = "1234"

    body = EmailService._build_text_body(ttl, code)

    assert "1234" in body
    assert "5" in body
    assert "expires" in body


def test_build_html_body():
    ttl = 5
    code = "1234"

    body = EmailService._build_html_body(ttl, code)

    assert "1234" in body
    assert "<h2>" in body
    assert "5" in body
