from typing import Optional
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os
from pathlib import Path

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@ofotolab.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_TLS=True,
    MAIL_SSL=False,
    TEMPLATE_FOLDER=Path(__file__).parent / 'email/templates'
)

class EmailService:
    def __init__(self):
        self.fastmail = FastMail(conf)
    
    async def send_verification_email(
        self,
        email: EmailStr,
        token: str,
        first_name: Optional[str] = None
    ):
        """Send verification email to user"""
        verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/verify-email?token={token}"
        
        message = MessageSchema(
            subject="Verify your email address",
            recipients=[email],
            template_body={
                "first_name": first_name or "User",
                "verification_url": verification_url
            },
            subtype="html"
        )
        
        await self.fastmail.send_message(
            message,
            template_name="verification.html"
        )
    
    async def send_password_reset_email(
        self,
        email: EmailStr,
        token: str,
        first_name: Optional[str] = None
    ):
        """Send password reset email to user"""
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/reset-password?token={token}"
        
        message = MessageSchema(
            subject="Reset your password",
            recipients=[email],
            template_body={
                "first_name": first_name or "User",
                "reset_url": reset_url
            },
            subtype="html"
        )
        
        await self.fastmail.send_message(
            message,
            template_name="password_reset.html"
        )
    
    async def send_organization_approval_email(
        self,
        email: EmailStr,
        org_name: str,
        first_name: Optional[str] = None
    ):
        """Send organization approval notification"""
        message = MessageSchema(
            subject=f"Organization {org_name} Approved",
            recipients=[email],
            template_body={
                "first_name": first_name or "User",
                "org_name": org_name,
                "login_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/login"
            },
            subtype="html"
        )
        
        await self.fastmail.send_message(
            message,
            template_name="org_approval.html"
        )
    
    async def send_organization_invitation_email(
        self,
        email: EmailStr,
        org_name: str,
        invite_token: str,
        first_name: Optional[str] = None
    ):
        """Send organization invitation email"""
        accept_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/accept-invite?token={invite_token}"
        
        message = MessageSchema(
            subject=f"Invitation to join {org_name}",
            recipients=[email],
            template_body={
                "first_name": first_name or "User",
                "org_name": org_name,
                "accept_url": accept_url
            },
            subtype="html"
        )
        
        await self.fastmail.send_message(
            message,
            template_name="org_invitation.html"
        )
