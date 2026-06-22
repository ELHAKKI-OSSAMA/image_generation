from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from uuid import UUID
import secrets
import re
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_, or_, func, delete
from sqlalchemy.orm import load_only, joinedload, selectinload

from fastapi import HTTPException, status, Request

from database.models.user import User
from database.models.session import Session
from database.models.password_reset import PasswordResetToken
from database.models.admin import Admin
from database.models.organization import Organization, OrganizationMember
from database.models.audit import AuditLog, RateLimit
from database.models.enums import (
    UserRole, VerificationStatus, AuditCategory, AuditAction,
    RATE_LIMIT_SETTINGS, TOKEN_EXPIRATION, PASSWORD_VALIDATION, SESSION_SETTINGS,
    OrganizationStatus
)
from database.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address"""
        stmt = select(User).where(User.email == email).options(
            load_only(
                User.id,
                User.email,
                User.password_hash,
                User.first_name,
                User.last_name,
                User.role,
                User.status,
                User.is_verified,
                User.created_at,
                User.updated_at
            ),
            joinedload(User.organization_memberships).joinedload(OrganizationMember.organization)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password using Argon2"""
        return pwd_context.hash(password)

    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Validate password strength against security requirements"""
        if len(password) < PASSWORD_VALIDATION["min_length"]:
            return False, f"Password must be at least {PASSWORD_VALIDATION['min_length']} characters long"
        if len(password) > PASSWORD_VALIDATION["max_length"]:
            return False, f"Password must be at most {PASSWORD_VALIDATION['max_length']} characters long"
        if PASSWORD_VALIDATION["require_uppercase"] and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if PASSWORD_VALIDATION["require_lowercase"] and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if PASSWORD_VALIDATION["require_numbers"] and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        if PASSWORD_VALIDATION["require_special"] and not any(c in PASSWORD_VALIDATION["special_chars"] for c in password):
            return False, f"Password must contain at least one special character ({PASSWORD_VALIDATION['special_chars']})"
        return True, "Password meets requirements"
    
    async def create_audit_log(
        self,
        action: AuditAction,
        category: AuditCategory,
        user_id: Optional[UUID] = None,
        details: Optional[str] = None,
        request: Optional[Request] = None
    ) -> None:
        """Create an audit log entry"""
        # Get request details
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host
            user_agent = request.headers.get("user-agent")

        # Create log entry
        log = AuditLog(
            action=action,
            category=category,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        self.db.add(log)
        await self.db.commit()

    async def check_rate_limit(
        self,
        key: str,
        category: str,
        identifier: str
    ) -> bool:
        """Check if a rate limit has been exceeded"""
        # Get rate limit settings
        settings = RATE_LIMIT_SETTINGS.get(category, {
            "max_attempts": 5,
            "window_seconds": 300  # 5 minutes
        })
        
        # Create composite key
        composite_key = f"{category}:{key}:{identifier}"
        
        # Get current count and window start
        stmt = select(RateLimit).where(RateLimit.key == composite_key)
        result = await self.db.execute(stmt)
        rate_limit = result.scalar_one_or_none()
        
        now = datetime.now(timezone.utc)
        
        if not rate_limit:
            # First attempt
            rate_limit = RateLimit(
                key=composite_key,
                attempts=1,
                window_start=now,
                last_attempt=now
            )
            self.db.add(rate_limit)
            await self.db.commit()
            return True
            
        # Check if window has expired
        window_seconds = settings["window_seconds"]
        if (now - rate_limit.window_start).total_seconds() > window_seconds:
            # Reset window
            rate_limit.attempts = 1
            rate_limit.window_start = now
            rate_limit.last_attempt = now
            await self.db.commit()
            return True
            
        # Check if max attempts exceeded
        if rate_limit.attempts >= settings["attempts"]:
            return False
            
        # Increment attempts
        rate_limit.attempts += 1
        rate_limit.last_attempt = now
        await self.db.commit()
        
        return True

    async def cleanup_rate_limits(self) -> None:
        """Clean up expired rate limits"""
        now = datetime.now(timezone.utc)
        
        # Delete rate limits older than the maximum window
        max_window = max(
            settings["window_seconds"] 
            for settings in RATE_LIMIT_SETTINGS.values()
        )
        
        stmt = delete(RateLimit).where(
            RateLimit.window_start < now - timedelta(seconds=max_window)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        await self.db.execute(
            delete(Session).where(
                or_(
                    Session.expires_at < datetime.now(timezone.utc),
                    Session.is_valid == False
                )
            )
        )
        await self.db.commit()

    async def cleanup_expired_tokens(self) -> None:
        """Clean up expired tokens"""
        now = datetime.utcnow()
        
        # Delete expired password reset tokens
        await self.db.execute(
            delete(PasswordResetToken).where(
                PasswordResetToken.expires_at < now
            )
        )
        
        # Update users with expired verification tokens
        await self.db.execute(
            update(User).where(
                and_(
                    User.verification_token_expires_at < now,
                    User.verification_token.isnot(None)
                )
            ).values(
                verification_token=None,
                verification_token_expires_at=None
            )
        )
        
        await self.db.commit()

    async def authenticate_user(
        self,
        email: str,
        password: str,
        request: Optional[Request] = None
    ) -> Optional[User]:
        """Authenticate a user with email and password"""
        # Check rate limits
        ip_address = request.client.host if request else "unknown"
        if not await self.check_rate_limit("login", "login", ip_address):
            await self.create_audit_log(
                action=AuditAction.RATE_LIMIT_EXCEEDED,
                category=AuditCategory.SECURITY,
                details=f"Rate limit exceeded for login from IP {ip_address}",
                request=request
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )

        # Get user by email
        stmt = select(User).where(User.email == email).options(
            load_only(
                User.id,
                User.email,
                User.password_hash,
                User.first_name,
                User.last_name,
                User.role,
                User.status,
                User.is_verified,
                User.created_at,
                User.updated_at
            ),
            joinedload(User.organization_memberships).joinedload(OrganizationMember.organization)
        )
        result = await self.db.execute(stmt)
        user = result.unique().scalar_one_or_none()
        
        if not user:
            await self.create_audit_log(
                action=AuditAction.LOGIN_FAILED,
                category=AuditCategory.AUTH,
                details=f"Login attempt with non-existent email: {email}",
                request=request
            )
            return None

        # Check if account is locked
        user = await self.db.execute(
            select(User).where(User.id == user.id)
        )
        user = user.scalar_one()
        if user.failed_login_attempts >= SESSION_SETTINGS["max_failed_attempts"]:
            lockout_time = user.last_failed_login + timedelta(seconds=SESSION_SETTINGS["lockout_duration"])
            if datetime.utcnow() < lockout_time:
                await self.create_audit_log(
                    action=AuditAction.LOGIN_FAILED,
                    category=AuditCategory.AUTH,
                    user_id=user.id,
                    details="Account temporarily locked due to too many failed attempts",
                    request=request
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is temporarily locked. Please try again later."
                )
            else:
                # Reset failed attempts after lockout period
                user.failed_login_attempts = 0
            
        # Check password
        if not self.verify_password(password, user.password_hash):
            # Update failed login attempts
            user.failed_login_attempts += 1
            user.last_failed_login = datetime.utcnow()
            await self.db.commit()

            await self.create_audit_log(
                action=AuditAction.LOGIN_FAILED,
                category=AuditCategory.AUTH,
                user_id=user.id,
                details="Invalid password",
                request=request
            )
            return None
            
        # Check verification status
        # if not user.is_verified:
        #     await self.create_audit_log(
        #         action=AuditAction.LOGIN_FAILED,
        #         category=AuditCategory.AUTH,
        #         user_id=user.id,
        #         details="Attempt to login with unverified email",
        #         request=request
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Email not verified"
        #     )
            
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        await self.db.commit()

        await self.create_audit_log(
            action=AuditAction.LOGIN,
            category=AuditCategory.AUTH,
            user_id=user.id,
            details="Successful login",
            request=request
        )
        
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def create_session(
        self,
        user_id: UUID,
        request: Request,
        remember_me: bool = False
    ) -> Session:
        """Create a new session for a user"""
        # Generate tokens
        access_token = self.create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(minutes=30)  # Access token expires in 30 minutes
        )
        refresh_token = secrets.token_urlsafe(32)
        
        # Create session
        session = Session(
            user_id=user_id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30 if remember_me else 1)
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session

    async def validate_session(
        self,
        token: str,
        request: Optional[Request] = None
    ) -> Optional[Session]:
        """Validate a session token"""
        # Check rate limits for API requests
        if request:
            ip_address = request.client.host
            if not await self.check_rate_limit("api", "api", ip_address):
                await self.create_audit_log(
                    action=AuditAction.RATE_LIMIT_EXCEEDED,
                    category=AuditCategory.SECURITY,
                    details=f"API rate limit exceeded for IP {ip_address}",
                    request=request
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later."
                )

        stmt = select(Session).where(
            and_(
                Session.token == token,
                Session.is_valid == True,
                Session.expires_at > datetime.utcnow()
            )
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if session:
            # Update last activity
            session.updated_at = datetime.utcnow()
            await self.db.commit()
        else:
            # Log invalid session attempt
            await self.create_audit_log(
                action=AuditAction.SESSION_INVALIDATED,
                category=AuditCategory.SESSION,
                details="Invalid session token used",
                request=request
            )

        return session
    
    async def refresh_session(
        self,
        refresh_token: str,
        request: Request
    ) -> Session:
        """Refresh a session using a valid refresh token"""
        # Get existing session
        old_session = await self.db.execute(
            select(Session)
            .options(
                joinedload(Session.user).joinedload(User.organization_memberships).joinedload(OrganizationMember.organization)
            )  # Eagerly load all required relationships
            .where(
                Session.refresh_token == refresh_token,
                Session.is_valid == True,
                Session.expires_at > datetime.now(timezone.utc)
            )
        )
        old_session = old_session.unique().scalar_one_or_none()  # Add .unique() to deduplicate results
        
        if not old_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Create new JWT access token
        new_access_token = self.create_access_token(
            data={"sub": str(old_session.user_id)},
            expires_delta=timedelta(minutes=30)
        )
        new_refresh_token = secrets.token_urlsafe(32)
        
        # Create new session
        new_session = Session(
            user_id=old_session.user_id,
            token=new_access_token,
            refresh_token=new_refresh_token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        # Invalidate old session
        old_session.is_valid = False
        old_session.updated_at = datetime.now(timezone.utc)
        
        # Save changes
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        await self.db.refresh(new_session.user)  # Make sure user is loaded
        
        return new_session

    async def invalidate_session(
        self,
        token: str,
        request: Optional[Request] = None,
        by_refresh_token: bool = False
    ) -> None:
        """Invalidate a specific session"""
        if by_refresh_token:
            stmt = update(Session).where(Session.refresh_token == token).values(is_valid=False)
        else:
            stmt = update(Session).where(Session.token == token).values(is_valid=False)
        
        await self.db.execute(stmt)
        await self.db.commit()

        await self.create_audit_log(
            action=AuditAction.SESSION_INVALIDATED,
            category=AuditCategory.SESSION,
            details="Session manually invalidated",
            request=request
        )
    
    async def invalidate_all_user_sessions(
        self,
        user_id: UUID,
        request: Optional[Request] = None
    ) -> None:
        """Invalidate all sessions for a user"""
        stmt = update(Session).where(Session.user_id == user_id).values(is_valid=False)
        await self.db.execute(stmt)
        await self.db.commit()

        await self.create_audit_log(
            action=AuditAction.SESSION_INVALIDATED,
            category=AuditCategory.SESSION,
            user_id=user_id,
            details="All user sessions invalidated",
            request=request
        )

    async def generate_verification_token(self) -> tuple[str, datetime]:
        """Generate a verification token for email verification"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION["verification_token"])
        return token, expires_at

    async def verify_email(
        self,
        token: str,
        request: Optional[Request] = None
    ) -> bool:
        """Verify a user's email address using a verification token"""
        stmt = select(User).where(
            and_(
                User.verification_token == token,
                User.verification_token_expires_at > datetime.utcnow(),
                User.status == VerificationStatus.PENDING
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            await self.create_audit_log(
                action=AuditAction.EMAIL_VERIFICATION_REQUEST,
                category=AuditCategory.AUTH,
                details="Invalid or expired verification token used",
                request=request
            )
            return False
            
        user.is_verified = True
        user.status = VerificationStatus.ACTIVE
        user.verification_token = None
        user.verification_token_expires_at = None
        
        await self.db.commit()

        await self.create_audit_log(
            action=AuditAction.EMAIL_VERIFIED,
            category=AuditCategory.AUTH,
            user_id=user.id,
            details="Email successfully verified",
            request=request
        )

        return True

    async def resend_verification_email(
        self,
        user_id: UUID,
        request: Optional[Request] = None
    ) -> tuple[str, datetime]:
        """Generate a new verification token for a user"""
        # Check rate limits
        if not await self.check_rate_limit("email_verification", "email_verification", str(user_id)):
            await self.create_audit_log(
                action=AuditAction.RATE_LIMIT_EXCEEDED,
                category=AuditCategory.SECURITY,
                user_id=user_id,
                details="Email verification rate limit exceeded",
                request=request
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many verification attempts. Please try again later."
            )

        # Generate new token
        token, expires_at = await self.generate_verification_token()

        # Update user
        stmt = update(User).where(
            and_(
                User.id == user_id,
                User.status == VerificationStatus.PENDING
            )
        ).values(
            verification_token=token,
            verification_token_expires_at=expires_at
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found or already verified"
            )

        await self.create_audit_log(
            action=AuditAction.EMAIL_VERIFICATION_REQUEST,
            category=AuditCategory.AUTH,
            user_id=user_id,
            details="New verification email requested",
            request=request
        )

        return token, expires_at

    async def create_password_reset_token(
        self,
        email: str,
        request: Optional[Request] = None
    ) -> Optional[tuple[str, datetime]]:
        """Create a password reset token for a user"""
        # Check rate limits
        ip_address = request.client.host if request else "unknown"
        if not await self.check_rate_limit("password_reset", "password_reset", ip_address):
            await self.create_audit_log(
                action=AuditAction.RATE_LIMIT_EXCEEDED,
                category=AuditCategory.SECURITY,
                details=f"Password reset rate limit exceeded for IP {ip_address}",
                request=request
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many reset attempts. Please try again later."
            )

        # Get user
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal that the email doesn't exist
            return None

        # Generate token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION["password_reset_token"])

        # Create reset token
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(reset_token)
        await self.db.commit()

        await self.create_audit_log(
            action=AuditAction.PASSWORD_RESET_REQUEST,
            category=AuditCategory.AUTH,
            user_id=user.id,
            details="Password reset requested",
            request=request
        )

        return token, expires_at

    async def validate_password_reset_token(
        self,
        token: str,
        request: Optional[Request] = None
    ) -> Optional[UUID]:
        """Validate a password reset token"""
        stmt = select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.expires_at > datetime.utcnow(),
                PasswordResetToken.used_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            await self.create_audit_log(
                action=AuditAction.PASSWORD_RESET_REQUEST,
                category=AuditCategory.AUTH,
                details="Invalid or expired password reset token used",
                request=request
            )
            return None

        return reset_token.user_id

    async def reset_password(
        self,
        token: str,
        new_password: str,
        request: Optional[Request] = None
    ) -> bool:
        """Reset a user's password using a reset token"""
        # Validate password strength
        is_valid, message = self.validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Get and validate token
        stmt = select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.expires_at > datetime.utcnow(),
                PasswordResetToken.used_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            await self.create_audit_log(
                action=AuditAction.PASSWORD_RESET_COMPLETE,
                category=AuditCategory.AUTH,
                details="Invalid or expired password reset token used",
                request=request
            )
            return False

        # Update password
        password_hash = self.get_password_hash(new_password)
        await self.db.execute(
            update(User)
            .where(User.id == reset_token.user_id)
            .values(password_hash=password_hash)
        )

        # Mark token as used
        reset_token.used_at = datetime.utcnow()
        
        # Invalidate all sessions
        await self.invalidate_all_user_sessions(reset_token.user_id, request)
        
        await self.db.commit()

        await self.create_audit_log(
            action=AuditAction.PASSWORD_RESET_COMPLETE,
            category=AuditCategory.AUTH,
            user_id=reset_token.user_id,
            details="Password successfully reset",
            request=request
        )

        return True

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: UserRole,
        organization_name: Optional[str] = None,
        organization_type: Optional[str] = None,
        organization_description: Optional[str] = None,
        request: Optional[Request] = None
    ) -> User:
        """Register a new user"""
        # Check if email already exists
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Validate password strength
        is_valid, message = self.validate_password_strength(password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Hash password
        password_hash = self.get_password_hash(password)

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        verification_token_expires_at = datetime.utcnow() + timedelta(hours=24)

        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role=role,
            verification_token=verification_token,
            verification_token_expires_at=verification_token_expires_at,
            status=VerificationStatus.ACTIVE if role == UserRole.SUPER_ADMIN else VerificationStatus.PENDING,
            is_verified=role == UserRole.SUPER_ADMIN  # Auto-verify super admins
        )
        self.db.add(user)
        await self.db.flush()  # Get user.id without committing

        # If organization registration
        if role == UserRole.MEMBER:
            if not organization_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization name is required"
                )
            
            # Create organization
            organization = Organization(
                name=organization_name,
                description=organization_description,
                owner_id=user.id,
                status=OrganizationStatus.PENDING
            )
            self.db.add(organization)
            await self.db.flush()  
            # Create organization membership for owner
            org_member = OrganizationMember(
                user_id=user.id,
                organization_id=organization.id,
                role="owner",
                permissions={"owner": True}
            )
            self.db.add(org_member)
        elif role == UserRole.ADMIN:
            # Create admin record
            admin = Admin(
                user_id=user.id,
                permissions={},  # Default permissions, can be updated later
                #is_super_admin=False  # Default to false, can be updated by super admin
            )
            self.db.add(admin)
            
            if organization_name:
                # Create organization
                organization = Organization(
                    name=organization_name,
                    description=organization_description,
                    owner_id=user.id,
                    status=OrganizationStatus.PENDING
                    )
                
                self.db.add(organization)
                await self.db.flush()
                
                # Create organization membership for owner
                org_member = OrganizationMember(
                    user_id=user.id,
                    organization_id=organization.id,
                    role="owner",
                    permissions={"owner": True}
                )
                self.db.add(org_member)

        # Create audit log
        await self.create_audit_log(
            action=AuditAction.USER_REGISTERED,
            category=AuditCategory.USER,
            user_id=user.id,
            details=f"User registered with role {role}",
            request=request
        )

        await self.db.refresh(user)
        result = await self.db.execute(select(User)
            .where(User.id == user.id)
            .options(selectinload(User.organizations)
            ) )
            
        user = result.scalar_one()
        return user
