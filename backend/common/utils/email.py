from typing import List, Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..constants.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    EMAIL_FROM_ADDRESS
)

async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    cc: Optional[List[str]] = None
) -> bool:
    """
    Send an email asynchronously using aiosmtplib.
    Returns True if successful, False otherwise.
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL_FROM_ADDRESS
    message["To"] = to_email
    if cc:
        message["Cc"] = ", ".join(cc)

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        async with aiosmtplib.SMTP(
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            use_tls=True
        ) as smtp:
            await smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            await smtp.send_message(message)
        return True
    except Exception as e:
        # Log the error
        print(f"Failed to send email: {str(e)}")
        return False

def get_verification_email_template(
    user_name: str,
    verification_url: str
) -> str:
    """Return HTML template for verification email."""
    return f"""
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2>Verify Your Email</h2>
        <p>Hello {user_name},</p>
        <p>Please click the button below to verify your email address:</p>
        <a href="{verification_url}" 
           style="display: inline-block; padding: 10px 20px; 
                  background: #4CAF50; color: white; 
                  text-decoration: none; border-radius: 5px;">
            Verify Email
        </a>
        <p>Or copy and paste this link:</p>
        <p>{verification_url}</p>
        <p>This link will expire in 24 hours.</p>
    </div>
    """
