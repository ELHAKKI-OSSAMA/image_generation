from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, load_only
from sqlalchemy import and_, or_

from core.database import get_db
from api.v1.auth.dependencies import get_current_user, verify_org_access, get_current_admin
from services.organization_service import OrganizationService
from schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    OrganizationMemberResponse
)
from database.models import User, Organization, OrganizationMember
from database.models.enums import UserRole
from typing import Dict

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("", response_model=OrganizationResponse)
async def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new organization"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(403, "Only super admin can create organization")
    org_service = OrganizationService(db)
    organization = await org_service.create_organization(
        name=data.name,
        description=data.description,
        owner_id=current_user.id
    )
    return organization


@router.get("/owned", response_model=List[OrganizationResponse])
async def get_owned_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organizations owned by the current user"""
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER :
        raise HTTPException(403, "Only organization and member can get owned organizations")
    org_service = OrganizationService(db)
    organizations = await org_service.get_owned_organizations(current_user.id)
    return organizations


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization details"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can get organization details")
    org = await verify_org_access(org_id, current_user, db)
    return org

@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update organization details"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can update organization details")
    org_service = OrganizationService(db)
    org = await verify_org_access(org_id, current_user, db)
    
    # Only owner or admin can update organization
    if current_user.id != org.owner_id and current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(403, "Only owner can update organization")
    
    updated_org = await org_service.update_organization(
        org_id=org_id,
        name=data.name,
        description=data.description
    )
    return updated_org

@router.get("/users/{user_id}/organizations", response_model=List[OrganizationResponse])
async def get_user_organizations(
    user_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all organizations for a specific user (both owned and member of)"""
    if current_admin.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can get user organizations")
    admin_service = AdminService(db)
    return await admin_service.get_user_all_organizations(user_id)

@router.delete("/{org_id}")
async def delete_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an organization"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can delete organization")
    org_service = OrganizationService(db)
    org = await verify_org_access(org_id, current_user, db)
    
    # Only owner or admin can delete organization
    if current_user.id != org.owner_id and current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(403, "Only owner can delete organization")
    
    await org_service.delete_organization(org_id)
    return {"message": "Organization deleted successfully"}

@router.get("/{org_id}/members", response_model=List[OrganizationMemberResponse])
async def get_organization_members(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all members of an organization"""
    if current_user.role != UserRole.SUPER_ADMIN and current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(403, "Only super admin and organization can get organization members")
    org_service = OrganizationService(db)
    if current_user.role != UserRole.SUPER_ADMIN:
        await verify_org_access(org_id, current_user, db)
    members = await org_service.list_members(org_id)
    return members

@router.post("/{org_id}/members", response_model=OrganizationMemberResponse)
async def add_organization_member(
    org_id: UUID,
    data: OrganizationMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a member to organization"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can add organization members")
    org_service = OrganizationService(db)
    org = await verify_org_access(org_id, current_user, db)
    
    # Only owner or admin can add members
    if current_user.id != org.owner_id and current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(403, "Only owner can add members")
    
    member = await org_service.add_member(
        org_id=org_id,
        email=data.email,
        role=data.role
    )
    return member

@router.delete("/{org_id}/members/{user_id}")
async def remove_organization_member(
    org_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a member from organization"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can remove organization members")
    org_service = OrganizationService(db)
    org = await verify_org_access(org_id, current_user, db)
    
    # Only owner or admin can remove members
    if current_user.id != org.owner_id and current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(403, "Only owner can remove members")
    
    # Cannot remove owner
    if user_id == org.owner_id:
        raise HTTPException(400, "Cannot remove organization owner")
    
    await org_service.remove_member(org_id, user_id)
    return {"message": "Member removed successfully"}

@router.put("/{org_id}/members/{user_id}", response_model=OrganizationMemberResponse)
async def update_member_role(
    org_id: UUID,
    user_id: UUID,
    data: OrganizationMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a member's role"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can update organization members")
    org_service = OrganizationService(db)
    org = await verify_org_access(org_id, current_user, db)
    
    # Only owner or admin can update roles
    if current_user.id != org.owner_id and current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(403, "Only owner can update member roles")
    
    # Cannot update owner's role
    if user_id == org.owner_id:
        raise HTTPException(400, "Cannot update organization owner's role")
    
    member = await org_service.update_member_role(
        org_id=org_id,
        user_id=user_id,
        role=data.role
    )
    return member

@router.get("/my", response_model=List[OrganizationResponse])
async def get_my_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    """Get organizations where the current user is a member"""
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER :
        raise HTTPException(403, "Only organization and member can get my organizations")
    org_service = OrganizationService(db)
    organizations = await org_service.get_user_organizations(current_user.id)
    return organizations

@router.put("/{org_id}/members/{user_id}/permissions", response_model=OrganizationMemberResponse)
async def update_member_permissions(
    org_id: UUID,
    user_id: UUID,
    permissions_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can update organization members permissions")
    """Update a member's permissions including custom permissions"""
    org_service = OrganizationService(db)
    org = await verify_org_access(org_id, current_user, db)
    
    # Only owner or admin can update permissions
    if current_user.id != org.owner_id and current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(403, "Only owner or admin can update member permissions")
    
    # Cannot update owner's permissions
    if user_id == org.owner_id:
        raise HTTPException(400, "Cannot update organization owner's permissions")
    
    member = await org_service.update_member_permissions(
        org_id=org_id,
        user_id=user_id,
        permissions_data=permissions_data,
        admin_id=current_user.id
    )
    return member

@router.get("/user/{user_id}", response_model=Dict[UUID, List[OrganizationResponse]])
async def get_user_organization_data(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    """Get all organization data for a user (both owned and member of)"""
    org_service = OrganizationService(db)
    
    # Check if requesting user has permission
    if current_user.id != user_id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(403, "Not authorized to view other user's organizations")
    
    # Get all organizations for the user in a single query
    stmt = (
        select(Organization)
        .distinct()
        .outerjoin(
            OrganizationMember,
            and_(
                OrganizationMember.organization_id == Organization.id,
                OrganizationMember.user_id == user_id
            )
        )
        .join(
            User,
            Organization.owner_id == User.id
        )
        .where(
            or_(
                Organization.owner_id == user_id,
                OrganizationMember.user_id == user_id
            )
        )
        .options(
            selectinload(Organization.owner)
        )
    )
    
    result = await db.execute(stmt)
    organizations = result.scalars().unique().all()
    
    # Always return a dictionary, even if empty
    return {
        str(user_id): [OrganizationResponse.from_orm(org) for org in organizations]
    }