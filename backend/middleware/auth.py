from fastapi import HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from jose import JWTError, jwt
from functools import wraps
from datetime import datetime
import logging

from database.models import UserRole
from auth.postgresql_auth import SECRET_KEY, ALGORITHM

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="postgresql-auth/login")

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        exp: int = payload.get("exp")
        
        logger.debug(f"Decoded token payload: {payload}")

        if email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check token expiry
        if datetime.utcnow() > datetime.utcfromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"email": email, "role": role}
    except JWTError as e:
        logger.error(f"JWTError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def check_roles(allowed_roles: List[UserRole]):
    """Decorator to check if user has required role"""
    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = kwargs.get("token")

            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No authentication token provided",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            payload = verify_token(token)
            user_role = payload.get("role")
            
            if UserRole(user_role) not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to perform this action",
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def admin_only(func):
    """Decorator for admin-only routes"""
    return check_roles([UserRole.ADMIN])(func)

def super_admin_only(func):
    """Decorator for super-admin-only routes"""
    return check_roles([UserRole.SUPER_ADMIN])(func)

def organization_only(func):
    """Decorator for organization-only routes"""
    return check_roles([UserRole.ORGANIZATION])(func)

def admin_or_organization(func):
    """Decorator for routes accessible by both admin and organization"""
    return check_roles([UserRole.ADMIN, UserRole.ORGANIZATION])(func)

def authenticated(func):
    """Decorator for routes requiring any authenticated user"""
    return check_roles([UserRole.ADMIN, UserRole.ORGANIZATION, UserRole.USER])(func)
