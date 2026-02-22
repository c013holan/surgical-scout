"""
Email sender for Surgical Scout digest
"""

import smtplib
import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Optional, Dict
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailSender:
    """Handle sending HTML emails via Gmail SMTP"""

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds

    def __init__(self, sender_email: str, sender_password: str, recipient_email: str):
        """
        Initialize email sender

        Args:
            sender_email: Gmail address to send from
            sender_password: Gmail App Password (not regular password)
            recipient_email: Email address to send to
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

        logger.info(f"Initialized EmailSender: {sender_email} -> {recipient_email}")

    def send_digest(self, subject: str, body_html: str) -> bool:
        """
        Send HTML email digest with retry logic

        Args:
            subject: Email subject line
            body_html: HTML content for email body

        Returns:
            True if email sent successfully, False otherwise
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(f"Attempt {attempt}/{self.MAX_RETRIES}: Sending email...")

                # Create message
                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = self.sender_email
                message["To"] = self.recipient_email

                # Attach HTML content
                html_part = MIMEText(body_html, "html")
                message.attach(html_part)

                # Connect to Gmail SMTP server
                logger.debug(f"Connecting to {self.SMTP_SERVER}:{self.SMTP_PORT}")
                with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                    server.set_debuglevel(0)  # Set to 1 for verbose debugging

                    # Start TLS encryption
                    server.starttls()
                    logger.debug("TLS started")

                    # Login
                    server.login(self.sender_email, self.sender_password)
                    logger.debug("Login successful")

                    # Send email
                    server.sendmail(
                        self.sender_email,
                        self.recipient_email,
                        message.as_string()
                    )

                logger.info(f"Email sent successfully to {self.recipient_email}")
                return True

            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"Authentication failed: {e}")
                logger.error("Please check your Gmail App Password is correct")
                return False  # Don't retry authentication errors

            except smtplib.SMTPException as e:
                logger.error(f"SMTP error on attempt {attempt}: {e}")
                if attempt < self.MAX_RETRIES:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error("Max retries reached. Email not sent.")
                    return False

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt}: {e}")
                if attempt < self.MAX_RETRIES:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error("Max retries reached. Email not sent.")
                    return False

        return False

    def send_digest_with_images(self, subject: str, body_html: str, images: Dict[str, bytes]) -> bool:
        """
        Send HTML email digest with embedded images

        Args:
            subject: Email subject line
            body_html: HTML content for email body
            images: Dictionary mapping image IDs to image bytes

        Returns:
            True if email sent successfully, False otherwise
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(f"Attempt {attempt}/{self.MAX_RETRIES}: Sending email with {len(images)} images...")

                # Create message with related parts for inline images
                message = MIMEMultipart("related")
                message["Subject"] = subject
                message["From"] = self.sender_email
                message["To"] = self.recipient_email

                # Attach HTML content
                html_part = MIMEText(body_html, "html")
                message.attach(html_part)

                # Attach images as inline
                for img_id, img_bytes in images.items():
                    try:
                        img_part = MIMEImage(img_bytes)
                        img_part.add_header('Content-ID', f'<{img_id}>')
                        img_part.add_header('Content-Disposition', 'inline', filename=f'{img_id}.jpg')
                        message.attach(img_part)
                    except Exception as e:
                        logger.warning(f"Could not attach image {img_id}: {e}")
                        continue

                # Connect to Gmail SMTP server
                logger.debug(f"Connecting to {self.SMTP_SERVER}:{self.SMTP_PORT}")
                with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                    server.set_debuglevel(0)
                    server.starttls()
                    logger.debug("TLS started")

                    server.login(self.sender_email, self.sender_password)
                    logger.debug("Login successful")

                    server.sendmail(
                        self.sender_email,
                        self.recipient_email,
                        message.as_string()
                    )

                logger.info(f"Email with images sent successfully to {self.recipient_email}")
                return True

            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"Authentication failed: {e}")
                return False

            except smtplib.SMTPException as e:
                logger.error(f"SMTP error on attempt {attempt}: {e}")
                if attempt < self.MAX_RETRIES:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error("Max retries reached. Email not sent.")
                    return False

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt}: {e}")
                if attempt < self.MAX_RETRIES:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error("Max retries reached. Email not sent.")
                    return False

        return False


def send_digest(subject: str, body_html: str) -> bool:
    """
    Convenience function to send email digest

    Args:
        subject: Email subject line
        body_html: HTML content for email body

    Returns:
        True if email sent successfully, False otherwise
    """
    import os

    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    if not all([sender_email, sender_password, recipient_email]):
        raise ValueError(
            "Email configuration incomplete. Please set SENDER_EMAIL, "
            "SENDER_PASSWORD, and RECIPIENT_EMAIL in .env file"
        )

    sender = EmailSender(sender_email, sender_password, recipient_email)
    return sender.send_digest(subject, body_html)


def send_digest_with_images(subject: str, body_html: str, images: Dict[str, bytes] = None) -> bool:
    """
    Convenience function to send email digest with images

    Args:
        subject: Email subject line
        body_html: HTML content for email body
        images: Dictionary mapping image IDs to image bytes

    Returns:
        True if email sent successfully, False otherwise
    """
    import os

    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    if not all([sender_email, sender_password, recipient_email]):
        raise ValueError(
            "Email configuration incomplete. Please set SENDER_EMAIL, "
            "SENDER_PASSWORD, and RECIPIENT_EMAIL in .env file"
        )

    sender = EmailSender(sender_email, sender_password, recipient_email)

    if images:
        return sender.send_digest_with_images(subject, body_html, images)
    else:
        return sender.send_digest(subject, body_html)


if __name__ == "__main__":
    # Test the email sender
    from dotenv import load_dotenv
    import os

    load_dotenv(override=True)

    print("Testing Email Sender...\n")

    test_subject = "Surgical Scout - Test Email"
    test_body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            h1 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>Test Email</h1>
        <p>This is a test email from Surgical Scout.</p>
        <p>If you're reading this, the email system is working correctly!</p>
    </body>
    </html>
    """

    success = send_digest(test_subject, test_body)

    if success:
        print("Test email sent successfully!")
    else:
        print("Test email failed to send. Check logs for details.")
