"""
Email service that handles business logic for sending emails.
Uses MailpitClient for actual HTTP communication.
"""

import logging

from app.core.config import settings
from app.clients.mailpit_client import MailpitClient

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service that handles business logic for sending emails.
    Delegates HTTP communication to MailpitClient.
    """

    def __init__(self, mailpit_client: MailpitClient):
        """
        Initialize the email service.

        Args:
            mailpit_client: Client for communicating with Mailpit API
        """
        self.mailpit_client = mailpit_client

    async def send_activation_code(self, to_email: str, code: str) -> bool:
        """
        Send activation code email.

        Args:
            to_email: Recipient email address
            code: 4-digit activation code

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        ttl_minutes = settings.activation_code_ttl_seconds / 60

        logger.info(f"Sending activation code {code} to {to_email}")

        subject = "Your Activation Code"
        text_body = self._build_text_body(ttl_minutes=ttl_minutes, code=code)
        html_body = self._build_html_body(ttl_minutes=ttl_minutes, code=code)

        success = await self.mailpit_client.send_email(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )

        if success:
            logger.info(f"Activation code email sent successfully to {to_email}")
        else:
            logger.error(f"Failed to send activation code email to {to_email}")

        return success

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
