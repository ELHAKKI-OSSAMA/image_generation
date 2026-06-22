from datetime import datetime, timedelta
from typing import Dict, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import SecretStr
from core.database import get_db
from core.security import create_jwt_token as create_access_token, get_password_hash, verify_password
from database.models import (
    User, Session, UserRole, VerificationStatus, Admin, Organization, 
    OrganizationStatus, OrganizationMember, UserProfile, UserToken
)
from schemas.auth import Token, UserLogin, UserResponse, UserRegistrationResponse, OrganizationOwnerResponse, OrganizationMemberResponse
from schemas.user import UserCreate
from common.constants.permissions import get_role_permissions
from dotenv import load_dotenv
from pydantic import SecretStr
from jose import jwt, JWTError
from pydantic import BaseModel
from fastapi import Request
from database.models import User
from sqlalchemy import select
from fastapi import HTTPException
from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import os
from api.v1.auth.dependencies import get_current_user

load_dotenv()

class EmailRequest(BaseModel):
    email: str
"""
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = SecretStr(os.getenv("MAIL_PASSWORD")),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = int(os.getenv("MAIL_PORT")),  # convert to int
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS"),
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS"),
    USE_CREDENTIALS = os.getenv("USE_CREDENTIALS")
)
"""

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))  # valeur par défaut si non défini
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", 
    response_model=Union[UserRegistrationResponse, OrganizationOwnerResponse, OrganizationMemberResponse],
    response_model_by_alias=True)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Union[UserRegistrationResponse, OrganizationOwnerResponse, OrganizationMemberResponse]:
    """Register a new user based on their role"""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if organization exists
    if user_data.role == UserRole.ORGANIZATION:
        org_result = await db.execute(
            select(Organization).where(Organization.name == user_data.organization_name)
        )
        org = org_result.scalar_one_or_none()
        if org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization already exists"
            )
    
    if user_data.role == UserRole.MEMBER:
        org_result = await db.execute(
            select(Organization).where(Organization.name == user_data.organization_name)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization not found"
            )
    
    # Get default permissions for the role
    role_permissions = get_role_permissions(user_data.role)
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        permissions=role_permissions,
        status=VerificationStatus.PENDING if user_data.role != UserRole.SUPER_ADMIN else VerificationStatus.VERIFIED,
        is_verified=False if user_data.role != UserRole.SUPER_ADMIN else True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    if user_data.role == UserRole.USER:
        # Create initial token record for the user
        user_token = UserToken(
            user_id=user.id,
            token=int(os.getenv("TOKEN_INITIAL_VALUE"))  # Initial token value
        )
        db.add(user_token)
        await db.commit()
    
    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        full_name=f"{user_data.first_name or ''} {user_data.last_name or ''}".strip() or None,
        timezone='UTC',
        avatar_url=f'https://ui-avatars.com/api/?name={user_data.first_name or ""}+{user_data.last_name or ""}&background=random',
        two_factor_enabled=False
    )
    db.add(profile)
    await db.commit()
    
    # Handle different registration types
    if user_data.role == UserRole.SUPER_ADMIN:
        # Create admin record
        admin = Admin(
            user_id=user.id,
            role=UserRole.SUPER_ADMIN,
            permissions={
                "manage_users": True,
                "manage_organizations": True,
                "manage_admins": True,
                "view_system_stats": True,
                "manage_content": True,
                "manage_settings": True
            }
        )
        db.add(admin)
        await db.commit()
        await db.refresh(user)
        return UserRegistrationResponse.model_validate(user)
        
    elif user_data.role == UserRole.ORGANIZATION:
        if not user_data.organization_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name is required for organization accounts"
            )
        # Create organization
        org = Organization(
            name=user_data.organization_name,
            description=user_data.organization_description,
            owner_id=user.id,
            status=OrganizationStatus.PENDING #OrganizationStatus.PENDING
        )
        print(f"Debug - Before org add: org.id = {org.id}")
        db.add(org)
        await db.commit()  # Commit organization first
        await db.refresh(org)
        print(f"Debug - After org commit: org.id = {org.id}")
        
        # Create admin record for organization owner
        admin = Admin(
            user_id=user.id,
            role=UserRole.ADMIN,
            permissions={
                "manage_organization": True,
                "manage_members": True,
                "view_organization": True,
                "view_members": True,
                "manage_events": True,
                "view_events": True,
                "approve_members": True
            }
        )
        print(f"Debug - Before admin add: admin.id = {admin.id}")
        db.add(admin)
        await db.commit()  # Commit admin record
        await db.refresh(admin)
        print(f"Debug - After admin commit: admin.id = {admin.id}")
        
        # Create organization member record for owner
        org_member = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,  # Now org.id exists
            role=UserRole.ADMIN,
            email=user_data.email,  # Add required fields
            password_hash=user.password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            permissions={
                "manage_organization": True,
                "manage_members": True,
                "view_organization": True,
                "view_members": True,
                "manage_events": True,
                "view_events": True
            }
        )
        print(f"Debug - Before member add: org_member.id = {org_member.id}")
        db.add(org_member)
        await db.commit()
        print(f"Debug - After member commit: org_member.id = {org_member.id}")
        
        await db.refresh(user)
        # Load organization relationship
        await db.refresh(org, ["owner"])
        # Convert both models to dict and combine them
        user_dict = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "status": user.status,
            "is_verified": user.is_verified,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "organization": {
                "id": org.id,
                "name": org.name,
                "description": org.description,
                "owner_id": org.owner_id,
                "status": org.status,
                "approved_by": org.approved_by,
                "approved_at": org.approved_at,
                "created_at": org.created_at,
                "updated_at": org.updated_at,
                "owner": None  # Will be populated by from_attributes
            }
        }
        return OrganizationOwnerResponse.model_validate(user_dict)
        
    elif user_data.role == UserRole.MEMBER:
        # Validate organization exists
        org_result = await db.execute(
            select(Organization).where(Organization.name == user_data.organization_name)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization not found"
            )
        # Create organization member with user data
        member = OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            email=user_data.email,
            password_hash=user.password_hash,  # Copy from the user we just created
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role="member",
            status="pending"
        )
        db.add(member)
        await db.commit()
        await db.refresh(user)
        # Load organization relationship
        await db.refresh(org, ["owner"])
        # Convert both models to dict and combine them
        user_dict = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "status": user.status,
            "is_verified": user.is_verified,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "organization": {
                "id": org.id,
                "name": org.name,
                "description": org.description,
                "owner_id": org.owner_id,
                "status": org.status,
                "approved_by": org.approved_by,
                "approved_at": org.approved_at,
                "created_at": org.created_at,
                "updated_at": org.updated_at,
                "owner": None  # Will be populated by from_attributes
            }
        }
        return OrganizationMemberResponse.model_validate(user_dict)
        
    else:  # Regular USER
        return UserRegistrationResponse.model_validate(user)

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    # Get user
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )
    
    # Create access token with permissions
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "permissions": user.permissions
    }
    
    # Create tokens
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=30)
    )
    print("TOKEN GENERATED WITH SECRET: ----->>>>>>>", access_token) 
    # Generate refresh token (valid for 7 days)
    refresh_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=7)
    )
    
    # Create session
    session = Session(
        user_id=user.id,
        token=access_token,
        refresh_token=refresh_token,  # Add refresh token
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(session)
    await db.commit()
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="lax",
    )
    
    # Set refresh token cookie (7 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=604800,  # 7 days in seconds
        expires=604800,
        samesite="lax",
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "permissions": user.permissions
        }
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Refresh access token using refresh token cookie"""
    refresh_token = request.cookies.get("refresh_token")
    print(f"Refresh token from cookie: {refresh_token}")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    
    try:
        # Get session by refresh token
        query = (
            select(Session)
            .where(Session.refresh_token == refresh_token)
            .where(Session.is_valid == True)
            .where(Session.expires_at > datetime.utcnow())
        )
        print(f"SQL Query: {query}")
        
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        print(f"Found session: {session}")
        
        if not session:
            # Debug: Find any session with this refresh token
            debug_result = await db.execute(
                select(Session).where(Session.refresh_token == refresh_token)
            )
            debug_session = debug_result.scalar_one_or_none()
            print(f"Debug - Found any session: {debug_session}")
            print(f"Debug - Session valid: {debug_session.is_valid if debug_session else None}")
            print(f"Debug - Session expired: {debug_session.expires_at if debug_session else None}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get user
        result = await db.execute(select(User).where(User.id == session.user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "permissions": user.permissions
        }
        
        # Create new access token
        new_access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)
        )
        
        # Update session
        session.token = new_access_token
        session.expires_at = datetime.utcnow() + timedelta(days=7)  # Match refresh token expiry
        await db.commit()
        
        # Set new access token cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {new_access_token}",
            httponly=True,
            max_age=1800,
            expires=1800,
            samesite="lax",
        )
        
        # Set refresh token cookie (7 days)
        response.set_cookie(
            key="refresh_token",
            value=session.refresh_token,  # Keep existing refresh token
            httponly=True,
            max_age=604800,  # 7 days in seconds
            expires=604800,
            samesite="lax",
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "permissions": user.permissions,
                "is_verified": user.is_verified
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token"
        )

@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Logout user and invalidate session"""
    # Get access token from cookie
    access_token = request.cookies.get("access_token", "").replace("Bearer ", "")
    
    if access_token:
        # Invalidate session
        result = await db.execute(
            select(Session).where(Session.token == access_token)
        )
        session = result.scalar_one_or_none()
        if session:
            session.is_valid = False
            await db.commit()
    
    # Clear cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Successfully logged out"}

from fastapi import Query

@router.post("/create-user")
async def create_user(
    user_data: UserCreate,
    verify: bool = Query(False, description="Whether to verify the user immediately"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)

):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    await register(user_data, db)
    if verify:
        user = await db.execute(select(User).where(User.email == user_data.email))
        user = user.scalar_one_or_none()
        if user_data.role == UserRole.ORGANIZATION:
            result = await db.execute(select(Organization).where(Organization.owner_id == user.id))
            organization = result.scalar_one_or_none()
            if not organization:
                raise HTTPException(status_code=404, detail="Organization not found")
            organization.status = OrganizationStatus.ACTIVE
            await db.commit()

        user.status = VerificationStatus.VERIFIED
        user.is_verified = True
        await db.commit()
    return {"msg": "User created successfully!"}
            

"""

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """#Verify user email using verification token
"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
        
        # Get user from database instead of CSV
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.is_verified:
            return {"msg": "Account already verified."}
        
        if user.role == UserRole.ORGANIZATION:
            result = await db.execute(select(Organization).where(Organization.owner_id == user.id))
            organization = result.scalar_one_or_none()
            if not organization:
                raise HTTPException(status_code=404, detail="Organization not found")
            organization.status = OrganizationStatus.ACTIVE
            await db.commit()

        user.status = VerificationStatus.VERIFIED
        user.is_verified = True
        await db.commit()
        return {"msg": "Email verified successfully!"}
        
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")





@router.post("/send-verification-email")
async def send_verification_email(request_data: EmailRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """
#Send verification email to user
"""
    email = request_data.email
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"msg": "Account already verified."}
    token_data = {"email": email}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    verify_url = f"{request.base_url}api/v1/auth/verify-email?token={token}"
    
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Click the link to verify your account: {verify_url}",
        subtype="plain"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"msg": "Verification email sent"}
    

from fastapi import FastAPI
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uuid

app = FastAPI()

# Configuration SMTP
SMTP_SERVER = ******
SMTP_PORT = ******
SMTP_USERNAME = ******
SMTP_PASSWORD = ******
FROM_EMAIL = ******
TO_EMAIL = ******

@router.get("/send-email")
def send_email():
    try:
        # Création du message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Test SMTP depuis FastAPI"
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg["Reply-To"] = FROM_EMAIL
        msg["Return-Path"] = FROM_EMAIL
        msg["X-Mailer"] = "FastAPI SMTP Client"
        msg["Message-ID"] = f"<{uuid.uuid4()}@nextappli.net>"

        # Contenu du message
        text = "Ceci est un test SMTP depuis FastAPI."
        html = "<html><body><p><b>Ceci est un test SMTP depuis FastAPI.</b></p></body></html>"

        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        # Connexion et envoi
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())

        return {"message": "Email envoyé avec succès à ossamaelhakki@gmail.com"}

    except Exception as e:
        return {"error": str(e)}
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import jwt
import uuid







# 📤 Route: Send verification email
@router.post("/send-verification-email")
async def send_verification_email(request_data: EmailRequest, request: Request, db: AsyncSession = Depends(get_db)):
    email = request_data.email
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"msg": "Account already verified."}

    # Generate token and verification URL
    token_data = {"email": email}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    verify_url = f"{request.base_url}api/v1/auth/verify-email?token={token}"

    # Compose email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your email"
    msg["From"] = FROM_EMAIL
    msg["To"] = email
    msg["Reply-To"] = FROM_EMAIL
    msg["Return-Path"] = FROM_EMAIL
    msg["X-Mailer"] = "FastAPI SMTP Client"
    msg["Message-ID"] = f"<{uuid.uuid4()}@nextappli.net>"

    text = f"Click the link to verify your account: {verify_url}"
    html = f"""
    <html>
        <body>
            <h2>Email Verification</h2>
            <p>Click the link below to verify your account:</p>
            <a href="{verify_url}">{verify_url}</a>
        </body>
    </html>
    """

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, email, msg.as_string())
        return {"msg": "Verification email sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# ✅ Route: Verify email using token
@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"msg": "Account already verified."}

        # Activate organization if needed
        if user.role == UserRole.ORGANIZATION:
            result = await db.execute(select(Organization).where(Organization.owner_id == user.id))
            organization = result.scalar_one_or_none()
            if not organization:
                raise HTTPException(status_code=404, detail="Organization not found")
            organization.status = OrganizationStatus.ACTIVE

        user.status = VerificationStatus.VERIFIED
        user.is_verified = True
        await db.commit()

        return {"msg": "Email verified successfully!"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
