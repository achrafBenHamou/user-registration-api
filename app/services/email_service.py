"""
Email service that calls a third-party HTTP API to send emails.
This service treats email sending as an external HTTP service call,
"""

import logging
import httpx

from app.core.config import settings
from fastapi import status

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service that sends emails by calling a third-party HTTP API.
    """

    def __init__(self, client: httpx.AsyncClient):
        """
        Initialize the email service.

        Args:
            client: HTTP client for making requests to the third-party service
        """
        self.client = client
        self.api_url = settings.email_api_url
        self.api_key = settings.email_api_key
        self.timeout = settings.email_api_timeout

    async def send_activation_code(self, to_email: str, code: str):
        """
        Send activation code email via third-party HTTP API.

        Makes an HTTP request to the external email service.

        Args:
            to_email: Recipient email address
            code: 4-digit activation code

        Returns:
            None
        """
        ttl_minutes = settings.activation_code_ttl_seconds / 60

        try:
            logger.info(f"Calling third-party email API: {self.api_url}")
            logger.info(f"Sending activation code {code} to {to_email}")

            # Make HTTP POST request to third-party email service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://mailpit:8025/api/v1/send",
                    json={
                        "From": {"Email": settings.from_email},
                        "To": [{"Email": to_email}],
                        "Subject": "Test Email",
                        "Text": self._build_text_body(
                            ttl_minutes=ttl_minutes, code=code
                        ),
                        "HTML": self._build_html_body(
                            ttl_minutes=ttl_minutes, code=code
                        ),
                    },
                )

                response.raise_for_status()
            # Check response status
            if (
                status.HTTP_200_OK
                <= response.status_code
                < status.HTTP_300_MULTIPLE_CHOICES
            ):
                logger.info(
                    f"Third-party email API responded successfully: "
                    f"status={response.status_code}, email sent to {to_email}"
                )

        except httpx.TimeoutException:
            logger.error(
                f"Third-party email API timeout after {self.timeout}s: {self.api_url}"
            )

        except httpx.ConnectError as e:
            logger.error(
                f"Failed to connect to third-party email API {self.api_url}: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error calling third-party email API: {str(e)}")

    @staticmethod
    def _build_text_body(ttl_minutes: float, code: str) -> str:
        """
        Build the plain text body for the email.

        Args:
            ttl_minutes: Number of minutes before expiration
            code: 4-digit activation code

        Returns:
            dict: Payload for the HTTP request
        """

        return (
            f"Your activation code is: {code}\n\n"
            f"This code expires in {ttl_minutes} minute(s).\n\n"
            f"If you didn't request this code, please ignore this email."
        )

    @staticmethod
    def _build_html_body(ttl_minutes: float, code: str) -> str:
        """
        Build the HTML body for the email.

        Args:
            ttl_minutes: Number of minutes before expiration
            code: 4-digit activation code
        Returns:
            str: HTML body for the email
        """
        return f"""
        <h2>Your Activation Code</h2>
        
        <p>
            Your activation code is:
        </p>
        
        <p style="font-size: 24px; font-weight: bold; letter-spacing: 2px;">
            {code}
        </p>

<p>
    This code expires in <strong>{ttl_minutes} minute(s)</strong>.
</p>

<p style="color: #666; font-size: 14px;">
    If you didn’t request this code, please ignore this email.
</p>
"""
