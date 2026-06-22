from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from core.database import get_db
from database.models.user import User
from database.models.admin import Admin
from schemas.auth import TokenData
from services.auth_service import AuthService
from database.config import settings

# Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_token_from_cookie_or_header(request: Request) -> str:
    """Get token from cookie first, then fall back to Authorization header"""
    # Try cookie first
    token = request.cookies.get("access_token")
    if not token:
        # Fall back to Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

async def get_current_user(
    token: str = Depends(get_token_from_cookie_or_header),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(**payload)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    """Get the current authenticated admin user"""
    # Check if user is an admin
    stmt = select(Admin).where(Admin.user_id == current_user.id)
    result = await db.execute(stmt)
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an admin"
        )
    
    return admin

async def get_current_super_admin(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """Get the current authenticated super admin user"""
    # Check if admin has super admin permissions
    if not current_admin.permissions.get("role"== "super_admin") :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a super admin"
        )
    
    return current_admin

def validate_password(password: str) -> bool:
    """
    Validate password strength
    Returns True if password meets requirements, False otherwise
    """
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return False
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return False
    
    # Check for at least one special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False
    
    return True
