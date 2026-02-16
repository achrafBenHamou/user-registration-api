"""
Mailpit HTTP client for sending emails via Mailpit API.
This client handles the low-level HTTP communication with Mailpit.
"""

import logging
import httpx
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class MailpitClient:
    """
    HTTP client for interacting with Mailpit email service.
    Handles all HTTP communication logic with the Mailpit API.
    """

    def __init__(self, client: httpx.AsyncClient):
        """
        Initialize the Mailpit client.

        Args:
            client: HTTP client for making requests to Mailpit service
        """
        self.client = client
        self.api_url = settings.email_api_url
        self.timeout = settings.email_api_timeout

    async def send_email(
        self,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> bool:
        """
        Send an email via Mailpit HTTP API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            text_body: Plain text body
            html_body: HTML body (optional)
            from_email: Sender email (defaults to settings.from_email)
            from_name: Sender name (defaults to settings.from_name)

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        from_email = from_email or settings.from_email
        from_name = from_name or settings.from_name

        payload = {
            "From": {"Email": from_email, "Name": from_name},
            "To": [{"Email": to_email}],
            "Subject": subject,
            "Text": text_body,
        }

        if html_body:
            payload["HTML"] = html_body

        try:
            logger.info(f"Sending email to {to_email} via Mailpit API: {self.api_url}")

            response = await self.client.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            logger.info(
                f"Email sent successfully to {to_email} "
                f"(status: {response.status_code})"
            )
            return True

        except httpx.TimeoutException:
            logger.error(f"Mailpit API timeout after {self.timeout}s: {self.api_url}")
            return False

        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Mailpit API {self.api_url}: {str(e)}")
            return False

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Mailpit API returned error status {e.response.status_code}: {str(e)}"
            )
            return False

        except Exception as e:
            logger.error(f"Unexpected error calling Mailpit API: {str(e)}")
            return False
