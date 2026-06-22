from fastapi import APIRouter
from database.models import Permission
from database.models.organization import OrganizationMember

from sqlalchemy import null, select
from core.database import async_session
from pydantic import BaseModel
from core.database import get_db  # Ensure this returns an AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr
from database.models.organization import UserRole
from typing import List
from fastapi import HTTPException
from api.v1.auth.dependencies import get_current_user
from database.models import User

router = APIRouter(
    prefix="/permissions",
    tags=["permissions"]
)

class OrganizationMemberSchema(BaseModel):
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: UserRole
    permissions: Dict[str, bool]  # Assuming permissions are stored as key-value pairs
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    firebase_uid: Optional[str]

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
        OrmMode = True  # Enables ORM mode for Pydantic models
        
@router.get("/organization-member-info/{id}", response_model=List[OrganizationMemberSchema])
async def get_organization_members(id: UUID,current_user: User = Depends(get_current_user)):
    # get organization members
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get organization members")
    async with async_session() as session:
        result = await session.execute(select(OrganizationMember).where(OrganizationMember.id == id))
        members = result.scalars().all()
        return members

@router.get("/organization-member/{id}", response_model=Dict[str, bool])
async def get_member_permissions(id: UUID,current_user: User = Depends(get_current_user)):
    # get member permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get member permissions")
    async with async_session() as session:
        result = await session.execute(select(OrganizationMember.permissions).where(OrganizationMember.id == id))
        permissions = result.scalar_one_or_none()
        return permissions or {}



@router.get("/organization-members-info/{organization_id}", response_model=List[OrganizationMemberSchema])
async def get_members_by_organization(organization_id: UUID,current_user: User = Depends(get_current_user)):
    # get members by organization
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get members by organization")
    async with async_session() as session:
        result = await session.execute(select(OrganizationMember).where(OrganizationMember.organization_id == organization_id))
        members = result.scalars().all()
        return members

@router.get("/organization-members/{organization_id}", response_model=List[Dict[str, bool]])
async def get_permissions_by_organization(organization_id: UUID,current_user: User = Depends(get_current_user)):
    # get permissions by organization
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get permissions by organization")
    async with async_session() as session:
        result = await session.execute(select(OrganizationMember.permissions).where(OrganizationMember.organization_id == organization_id))
        permissions_list = result.scalars().all()
        return permissions_list or []


@router.get("/{id}")
async def get_permissions_by_id(id: int,current_user: User = Depends(get_current_user)):
    # get permissions by id
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get permissions by id")
    async with async_session() as session:
        result = await session.execute(select(Permission).where(Permission.id == id))
        permission = result.scalar_one_or_none()
        return permission
        
    
@router.get("/role/{role}")
async def get_permissions_by_role(role: str,current_user: User = Depends(get_current_user)):
    # get permissions by role
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get permissions by role")
    async with async_session() as session:
        result = await session.execute(select(Permission).where(Permission.role == role))
        permissions = result.scalars().all()
        return permissions

    
@router.get("/")
async def get_permissions(current_user: User = Depends(get_current_user)):
    # get permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get permissions")
    async with async_session() as session:
        result = await session.execute(select(Permission))
        permissions = result.scalars().all()
        return permissions

@router.post("/")
async def create_permission(
    permission: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # create permission
    # Check if the user is a superadmin
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create permissions")
    
    # Insert permission into database
    new_permission = Permission(
        name=permission.get("name"),
        description=permission.get("description"),
        role=permission.get("role"),
        type=permission.get("type"),
        created_at=datetime.utcnow()
    )
    
    db.add(new_permission)
    await db.commit()
    await db.refresh(new_permission)
    
    return new_permission
    
    
    



@router.get("/ui/{id}", response_model=Dict[str, List[Dict[str, str]]])
async def get_member_permissions(id: UUID,current_user: User = Depends(get_current_user)):
    # get member permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get member permissions")
    async with async_session() as session:
        # Fetch user's permissions from `organization_member` table
        result = await session.execute(select(OrganizationMember.permissions).where(OrganizationMember.id == id))
        user_permissions = result.scalar_one_or_none() or {}

        # Fetch permission mappings from the `permissions` table
        permission_results = await session.execute(select(Permission.type, Permission.name, Permission.description))
        permissions_data = permission_results.fetchall()

    # Group permissions by type dynamically
    grouped_permissions = {}
    for perm_type, name, desc in permissions_data:
        if perm_type in user_permissions:  # Include only relevant permissions
            active = str(user_permissions.get(perm_type, False))  # Convert to string

            if perm_type not in grouped_permissions:
                grouped_permissions[perm_type] = []  # Create group dynamically
            
            grouped_permissions[perm_type].append({
                "name": name,
                "desc": desc,
                "active": active  # Ensuring 'active' is a string
            })

    return grouped_permissions
