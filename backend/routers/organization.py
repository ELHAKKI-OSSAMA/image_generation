from fastapi import APIRouter
from database.models import Organization
from database.models.organization import OrganizationMember
from database.models.event import Event
from database.models.usage_statistic import UsageStatistic

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
from database.models import UserProfile, Session, User,Admin
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from fastapi import HTTPException,Response, Request
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.auth.routes import logout
from api.v1.auth.dependencies import get_current_user, verify_org_access, get_current_admin
from database.models import Image,Model

router = APIRouter(
    prefix="/organization",
    tags=["organization"]
)

class ModelResponse(BaseModel):
    id: int
    name: str
    description: str
    
    class Config:
        from_attributes = True
        OrmMode = True


@router.get("/member/permissions")
async def get_my_permissions(current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    # get my permissions
    if  current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER :
        raise HTTPException(status_code=403, detail="Only organization and member can get my permissions")
    
    result = await db.execute(
        select(User).where(User.id == current_user.id)
    )

    user = result.scalar_one_or_none()

    return user.permissions

@router.get("/")
async def get_organizations(db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    # get organizations
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can get organizations")
    result = await db.execute(select(Organization))
    organizations = result.scalars().all()
    return organizations

@router.get("/{id}")
async def get_organization(
    id: UUID,
    db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
    # get organization by id
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can get organizations")
    """Get organization details"""
    result = await db.execute(select(Organization).where(Organization.id == id))
    organization = result.scalar_one_or_none()
    return organization


@router.delete("/me")
async def delete_organization(response: Response, request: Request,current_user: User = Depends(get_current_user), org_id: str = Depends(verify_org_access), db: AsyncSession = Depends(get_db)):
    """Delete an organization and all related members, profiles, sessions, and users"""
    # Fetch the organization
    if current_user.role != UserRole.ORGANIZATION :
        raise HTTPException(status_code=403, detail="Only admin can delete organizations")
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not organization.owner_id:
        raise HTTPException(status_code=400, detail="Owner ID cannot be NULL")

    # Delete all events linked to the organization
    event_result = await db.execute(select(Event).where(Event.organization_id == organization.id))
    events = event_result.scalars().all()
    for event in events:
        await db.delete(event)

    # Delete all usage statistics linked to the organization
    stats_result = await db.execute(select(UsageStatistic).where(UsageStatistic.organization_id == id))
    stats = stats_result.scalars().all()
    for stat in stats:
        await db.delete(stat)
    await db.commit()

    # Fetch organization members
    member_result = await db.execute(select(OrganizationMember).where(OrganizationMember.organization_id == id))
    members = member_result.scalars().all()
    
    for member in members:
        user_id = member.user_id

        # Delete related profiles
        profile_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profiles = profile_result.scalars().all()
        for profile in profiles:
            await db.delete(profile)
        await db.commit()

        # Delete related sessions
        session_result = await db.execute(select(Session).where(Session.user_id == user_id))
        sessions = session_result.scalars().all()
        for session in sessions:
            await db.delete(session)
        await db.commit()

        # Delete related admin entries first
        admin_result = await db.execute(select(Admin).where(Admin.user_id == user_id))
        admins = admin_result.scalars().all()
        for admin in admins:
            await db.delete(admin)
        await db.commit()

        # Remove the member from OrganizationMember
        await db.delete(member)
        await db.commit()


    # Delete the organization itself
    await db.delete(organization)
    await db.commit()

    for member in members:
        user_id = member.user_id

        # Delete the user record
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            await db.delete(user)
        await db.commit()

    await logout(response=response, request=request, db=db)

    return {"message": "Organization and all related members, profiles, and sessions deleted successfully", "organization_id": str(id)}


@router.get("/me/count_members")
async def get_count_of_members_of_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # If org_id is not provided, try to get it from the current user's organization
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only Organization and Member can get images")
    
    # Get the user's organization ID from organization_members table
    org_member = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.status == 'active')  # Only active members
    )
    org_member = org_member.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not an active member of any organization")
    
    org_id = str(org_member)
    
    # Now query for images in the user's organization
    result = await db.execute(select(OrganizationMember).where(OrganizationMember.organization_id == org_id))
    members = result.scalars().all()
    
    return len(members)

@router.get("/models/used")
async def get_models_of_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # If org_id is not provided, try to get it from the current user's organization
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only Organization and Member can get images")
    
    # Get the user's organization ID from organization_members table
    org_member = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.status == 'active')  # Only active members
    )
    org_member = org_member.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not an active member of any organization")
    
    org_id = str(org_member)
    
    # Now query for images in the user's organization
    result = await db.execute(select(Model).where(Image.model_id == Model.id).distinct())
    models = result.scalars().all()
    
    
    return [ModelResponse.model_validate(model) for model in models]


@router.delete("/{id}")
async def delete_organization(id: UUID, response: Response,request: Request,current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    """Delete an organization and all related members, profiles, sessions, and users"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can delete organizations")    
    # Fetch the organization
    result = await db.execute(select(Organization).where(Organization.id == id))
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not organization.owner_id:
        raise HTTPException(status_code=400, detail="Owner ID cannot be NULL")

    # Delete all events linked to the organization
    event_result = await db.execute(select(Event).where(Event.organization_id == id))
    events = event_result.scalars().all()
    for event in events:
        await db.delete(event)

    # Delete all usage statistics linked to the organization
    stats_result = await db.execute(select(UsageStatistic).where(UsageStatistic.organization_id == id))
    stats = stats_result.scalars().all()
    for stat in stats:
        await db.delete(stat)
    await db.commit()

    # Fetch organization members
    member_result = await db.execute(select(OrganizationMember).where(OrganizationMember.organization_id == id))
    members = member_result.scalars().all()
    
    for member in members:
        user_id = member.user_id

        # Delete related profiles
        profile_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profiles = profile_result.scalars().all()
        for profile in profiles:
            await db.delete(profile)
        await db.commit()

        # Delete related sessions
        session_result = await db.execute(select(Session).where(Session.user_id == user_id))
        sessions = session_result.scalars().all()
        for session in sessions:
            await db.delete(session)
        await db.commit()

        # Delete related admin entries first
        admin_result = await db.execute(select(Admin).where(Admin.user_id == user_id))
        admins = admin_result.scalars().all()
        for admin in admins:
            await db.delete(admin)
        await db.commit()

        # Remove the member from OrganizationMember
        await db.delete(member)
        await db.commit()


    # Delete the organization itself
    await db.delete(organization)
    await db.commit()

    for member in members:
        user_id = member.user_id

        # Delete the user record
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            await db.delete(user)
        await db.commit()

    await logout(response=response, request=request, db=db)

    return {"message": "Organization and all related members, profiles, and sessions deleted successfully", "organization_id": str(id)}



@router.get("/member/{user_id}")
async def get_member_details(user_id: UUID, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Get full details of an organization member by user ID"""
    if current_user.role != UserRole.SUPER_ADMIN and current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only super admin and organization can get member details")
    result = await db.execute(
        select(OrganizationMember)
        .options(
            joinedload(OrganizationMember.user)
            .joinedload(User.profile),  # Load User and UserProfile
            joinedload(OrganizationMember.organization)  # Load Organization
        )
        .where(OrganizationMember.user_id == user_id)
    )

    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="User is not a member of any organization")

    user = member.user
    profile = user.profile
    organization = member.organization

    return {
        "full_name": profile.full_name if profile.full_name else f"{user.first_name} {user.last_name}",
        "email": user.email,
        "status": user.status,  # Enum handling
        "organization": organization.name if organization else None,
        "role": member.role.name if member else None,
        "organization_status": organization.status if organization else None,
        "member_status": member.status if member else None,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "permissions": user.permissions,
        "avatar_url": profile.avatar_url if profile else None
    }


@router.get("/members/{user_id}")
async def get_organization_members(user_id: UUID, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Get all members of the organization where this user belongs"""
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER :
        raise HTTPException(status_code=403, detail="Only organization and member can get organization members")
    org_id=select(OrganizationMember.organization_id).where(OrganizationMember.user_id == current_user.id)
    await verify_org_access(org_id, current_user, db)
    # Fetch the organization ID where the user is a member
    org_result = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == user_id)
    )
    organization_id = org_result.scalar_one_or_none()
    
    if not organization_id:
        raise HTTPException(status_code=404, detail="User is not part of any organization")

    # Fetch all members of the organization
    members_result = await db.execute(
        select(OrganizationMember)
        .options(
            joinedload(OrganizationMember.user)
            .joinedload(User.profile),  # Load User and UserProfile
            joinedload(OrganizationMember.organization)  # Load Organization
        )
        .where(OrganizationMember.organization_id == organization_id)
    )



    members = members_result.scalars().all()

    # Fetch current user details for permission validation
    user_result = await db.execute(select(OrganizationMember).where(OrganizationMember.user_id == user_id))
    current_user = user_result.scalar_one_or_none()
    


    # Check if the user has permission to view other members' permissions
    can_view_permissions = (
        current_user.role == "ADMIN" or 
        current_user.permissions.get("MANAGE_MEMBERS", False) or 
        current_user.permissions.get("view_members", False)
    )

    # Format response with full details of each member
    members_list = [
        {
            "full_name": member.user.profile.full_name if member.user.profile.full_name else f"{member.user.first_name} {member.user.last_name}",
            "email": member.user.email,
            "status": member.user.status,  # Enum handling
            "organization": member.organization.name if member.organization else None,
            "role": member.role.name if member.role else None,
            "organization_status": member.organization.status if member.organization else None,
            "member_status": member.status if member.status else None,
            "created_at": member.user.created_at,
            "last_login": member.user.last_login,
            "permissions": member.permissions if can_view_permissions else None, # Conditional permissions
            "avatar_url": member.user.profile.avatar_url if member.user.profile else None,
            "edit": member.user.permissions.get("MANAGE_MEMBERS", False) or member.role.name == "ADMIN"
        }
        for member in members
    ]

    return {"organization_id": str(organization_id), "members": members_list}
