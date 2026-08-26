import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class EmailService:
    """Small SMTP adapter with no new third-party dependency."""

    @staticmethod
    def is_configured():
        required = (
            os.getenv("SMTP_HOST"),
            os.getenv("SMTP_PORT"),
            os.getenv("SMTP_USERNAME"),
            os.getenv("SMTP_PASSWORD"),
            os.getenv("MAIL_FROM"),
        )
        return all(required)

    @staticmethod
    def send_password_reset(to_email, reset_url, expires_minutes):
        if not EmailService.is_configured():
            logger.error("Password reset email requested but SMTP is not configured.")
            return False

        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", "587"))
        username = os.getenv("SMTP_USERNAME")
        password = os.getenv("SMTP_PASSWORD")
        mail_from = os.getenv("MAIL_FROM")
        use_ssl = os.getenv("SMTP_USE_SSL", "false").strip().lower() in {"1", "true", "yes"}

        message = EmailMessage()
        message["Subject"] = "MINIFY GADGETS ERP – Password Reset"
        message["From"] = mail_from
        message["To"] = to_email
        message.set_content(
            "MINIFY GADGETS ERP V2\n\n"
            "We received a request to reset your ERP password.\n\n"
            f"Open this link to create a new password (valid for {expires_minutes} minutes):\n"
            f"{reset_url}\n\n"
            "If you did not request this, you can safely ignore this email.\n"
            "For security, never share this link with anyone.\n"
        )

        try:
            if use_ssl:
                with smtplib.SMTP_SSL(host, port, timeout=20) as smtp:
                    smtp.login(username, password)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(host, port, timeout=20) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                    smtp.login(username, password)
                    smtp.send_message(message)
            return True
        except Exception:
            logger.exception("Failed to send password reset email.")
            return False
