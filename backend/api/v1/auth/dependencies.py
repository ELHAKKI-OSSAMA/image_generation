from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import SECRET_KEY, ALGORITHM
from database.models.user import User, UserRole
from database.models.organization import OrganizationMember, Organization
from schemas.auth import TokenData
from database.models.event import Event
from sqlalchemy.orm import joinedload

async def get_token_from_cookie(request: Request) -> str:
    """Get token from cookie"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    return token

async def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        exp: int = payload.get("exp")

        if not all([user_id, email, role, exp]):
            raise credentials_exception

        token_data = TokenData(
            user_id=UUID(user_id),
            email=email,
            role=UserRole(role),
            exp=datetime.fromtimestamp(exp)
        )
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = await db.get(User, token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current authenticated admin user"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_current_org_member(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> OrganizationMember:
    """Get the current authenticated organization member"""
    member = await db.execute(
        select(OrganizationMember)
        .where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == org_id
        )
    )
    member = member.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    return member

async def verify_org_access(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Organization:
    """Verify access to an organization"""
    org = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = org.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    if current_user.role == UserRole.ADMIN:
        return org
        
    member = await get_current_org_member(org_id, current_user, db)
    return org

async def verify_event_access(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Verify access to an event"""
    # Get event and its organization
    event = await db.execute(
        select(Event)
        .where(Event.id == event_id)
        .options(joinedload(Event.organization))
    )
    event = event.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if current_user.role == UserRole.ADMIN:
        return {"event": event, "org": event.organization}
        
    # Verify organization membership
    member = await get_current_org_member(
        event.organization_id, 
        current_user, 
        db
    )
    
    return {
        "event": event,
        "org": event.organization,
        "member": member
    }
