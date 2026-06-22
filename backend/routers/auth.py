from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from uuid import UUID

from database import get_db
from models.user import User, UserCreate, UserResponse
from schemas.auth import UserRegistrationResponse
from services.auth_service import AuthService
from services.email_service import EmailService
from database.config import settings
from services.internal_log_service import InternalLogService
from models.log import LogBase, LogLevel, LogCategory
from database.models import UserRole, VerificationStatus

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    log_service = InternalLogService(db)
    
    try:
        # Check rate limit
        if not await auth_service.check_rate_limit(
            f"login:{request.client.host}",
            5,  # attempts
            300  # seconds
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts"
            )
        
        # Authenticate user
        user = await auth_service.authenticate_user(
            form_data.username,
            form_data.password
        )
        
        if not user:
            # Log failed login
            await log_service.create_log(LogBase(
                level=LogLevel.WARNING,
                category=LogCategory.SECURITY,
                action="LOGIN_FAILED",
                details=f"Failed login attempt for user: {form_data.username}",
                metadata={
                    "username": form_data.username,
                    "attempt_time": datetime.utcnow().isoformat()
                }
            ))
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create session
        session = await auth_service.create_session(
            user_id=user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        # Log successful login
        await log_service.create_log(LogBase(
            level=LogLevel.INFO,
            category=LogCategory.SECURITY,
            action="LOGIN_SUCCESS",
            details=f"Successful login for user: {user.email}",
            metadata={
                "user_id": str(user.id),
                "email": user.email,
                "login_time": datetime.utcnow().isoformat()
            }
        ))
        
        return {
            "access_token": session.token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        await log_service.create_log(LogBase(
            level=LogLevel.ERROR,
            category=LogCategory.SECURITY,
            action="LOGIN_ERROR",
            details=f"Error during login: {str(e)}",
            metadata={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.post("/register/{type}")
async def register(
    type: str,
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    email_service = EmailService()
    log_service = InternalLogService(db)
    
    try:
        # Validate registration type
        if type not in ["super-admin", "organization", "member", "user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid registration type"
            )
        
        # Check email uniqueness
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Start transaction
        async with db.begin():
            # Generate verification token
            verification_token, expires_at = await auth_service.generate_verification_token()
            
            # Create user
            user = User(
                email=user_data.email,
                password_hash=auth_service.get_password_hash(user_data.password),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=UserRole[type.upper()],
                verification_token=verification_token,
                verification_token_expires_at=expires_at
            )
            db.add(user)
            await db.flush()
            
            # Handle type-specific logic
            if type == "super-admin":
                admin = Admin(user_id=user.id, permissions={"super_admin": True})
                db.add(admin)
            elif type == "organization":
                org = Organization(
                    name=user_data.organization_name,
                    owner_id=user.id
                )
                db.add(org)
                await db.flush()
                
                member = OrganizationMember(
                    user_id=user.id,
                    organization_id=org.id,
                    role="admin"
                )
                db.add(member)
            elif type == "member":
                member = OrganizationMember(
                    user_id=user.id,
                    organization_id=user_data.organization_id,
                    role="member"
                )
                db.add(member)
        
        # Send verification email
        #background_tasks.add_task(
            # email_service.send_verification_email,
            # user.email,
            # verification_token
        #)
        
        # Reload user with relationships
        user = await auth_service.get_user_by_email(user.email)
        
        # Log registration
        await log_service.create_log(LogBase(
            level=LogLevel.INFO,
            category=LogCategory.SECURITY,
            action="REGISTRATION_SUCCESS",
            details=f"New {type} registration: {user.email}",
            metadata={
                "user_id": str(user.id),
                "email": user.email,
                "type": type,
                "registration_time": datetime.utcnow().isoformat()
            }
        ))
        
        return {
            "message": "Registration successful",
            "user": UserRegistrationResponse.from_orm(user)
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        await log_service.create_log(LogBase(
            level=LogLevel.ERROR,
            category=LogCategory.SECURITY,
            action="REGISTRATION_ERROR",
            details=f"Error during registration: {str(e)}",
            metadata={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.post("/refresh-token")
async def refresh_token(
    request: Request,
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        # Create new session
        session = await auth_service.refresh_session(refresh_token)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": session.token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while refreshing the token"
        )

@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    log_service = InternalLogService(db)
    
    try:
        # Verify email
        success = await auth_service.verify_email(token)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Log verification
        await log_service.create_log(LogBase(
            level=LogLevel.INFO,
            category=LogCategory.SECURITY,
            action="EMAIL_VERIFICATION",
            details="Email verification successful",
            metadata={
                "token": token,
                "verification_time": datetime.utcnow().isoformat()
            }
        ))
        
        return {"message": "Email verified successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        await log_service.create_log(LogBase(
            level=LogLevel.ERROR,
            category=LogCategory.SECURITY,
            action="EMAIL_VERIFICATION_ERROR",
            details=f"Error during email verification: {str(e)}",
            metadata={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during email verification"
        )

@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    log_service = InternalLogService(db)
    
    try:
        # Get token from header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )
        
        token = authorization.split(" ")[1]
        
        # Invalidate session
        await auth_service.invalidate_session(token)
        
        # Log logout
        await log_service.create_log(LogBase(
            level=LogLevel.INFO,
            category=LogCategory.SECURITY,
            action="LOGOUT",
            details="User logged out successfully",
            metadata={
                "logout_time": datetime.utcnow().isoformat()
            }
        ))
        
        return {"message": "Logged out successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        await log_service.create_log(LogBase(
            level=LogLevel.ERROR,
            category=LogCategory.SECURITY,
            action="LOGOUT_ERROR",
            details=f"Error during logout: {str(e)}",
            metadata={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout"
        )
