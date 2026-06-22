from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status, Request
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from database.models import User, Organization, OrganizationMember, UserProfile
from database.models.enums import OrganizationStatus, UserRole, AuditCategory, AuditAction
from services.auth_service import AuthService

class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)

    async def create_organization(
        self,
        name: str,
        description: Optional[str],
        owner_id: UUID,
        request: Optional[Request] = None
    ) -> Organization:
        """Create a new organization"""
        # Check if organization name is unique
        query = (
            select(Organization)
            .where(Organization.name == name)
        )
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this name already exists"
            )

        # Create organization
        org = Organization(
            name=name,
            description=description,
            owner_id=owner_id,
            status=OrganizationStatus.pending
        )
        self.db.add(org)
        
        # Create owner membership
        member = OrganizationMember(
            user_id=owner_id,
            organization_id=org.id,
            role=UserRole.admin,
            permissions={"admin": True}
        )
        self.db.add(member)
        
        await self.db.commit()
        await self.db.refresh(org)

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.create,
            category=AuditCategory.organization,
            user_id=owner_id,
            details=f"Created organization: {name}",
            request=request
        )

        return org

    async def get_organization(self, org_id: UUID) -> Optional[Organization]:
        """Get organization with eager loaded members and owner"""
        query = (
            select(Organization)
            .options(
                joinedload(Organization.owner),
                selectinload(Organization.members).joinedload(OrganizationMember.user)
            )
            .where(Organization.id == org_id)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_organization_by_name(self, name: str) -> Optional[Organization]:
        """Get organization by name"""
        query = (
            select(Organization)
            .where(Organization.name == name)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_organization(
        self,
        org_id: UUID,
        data: Dict[str, Any],
        user_id: UUID,
        request: Optional[Request] = None
    ) -> Organization:
        """Update organization details"""
        org = await self.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check permissions
        if not await self.is_admin(org_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update organization"
            )

        # Update fields
        for field, value in data.items():
            if hasattr(org, field):
                setattr(org, field, value)

        await self.db.commit()
        await self.db.refresh(org)

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.update,
            category=AuditCategory.organization,
            user_id=user_id,
            details=f"Updated organization: {org.name}",
            request=request
        )

        return org

    async def delete_organization(
        self,
        org_id: UUID,
        user_id: UUID,
        request: Optional[Request] = None
    ) -> None:
        """Delete an organization"""
        org = await self.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check permissions
        if not await self.is_owner(org_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization owner can delete organization"
            )

        # Delete organization (cascade will handle members)
        await self.db.delete(org)
        await self.db.commit()

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.delete,
            category=AuditCategory.organization,
            user_id=user_id,
            details=f"Deleted organization: {org.name}",
            request=request
        )

    async def add_member(
        self,
        org_id: UUID,
        user_id: UUID,
        role: UserRole,
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> OrganizationMember:
        """Add a member to organization"""
        # Check if organization exists
        org = await self.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check admin permissions
        if not await self.is_admin(org_id, admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add members"
            )

        # Check if user exists
        query = (
            select(User)
            .where(User.id == user_id)
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if already a member
        query = (
            select(OrganizationMember)
            .where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id
                )
            )
        )
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member"
            )

        # Add member
        member = OrganizationMember(
            user_id=user_id,
            organization_id=org_id,
            role=role,
            permissions={}
        )
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.create,
            category=AuditCategory.organization_member,
            user_id=admin_id,
            details=f"Added member {user.email} to {org.name}",
            request=request
        )

        return member

    async def remove_member(
        self,
        org_id: UUID,
        user_id: UUID,
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> None:
        """Remove a member from organization"""
        # Check if organization exists
        org = await self.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check admin permissions
        if not await self.is_admin(org_id, admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to remove members"
            )

        # Cannot remove owner
        if user_id == org.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove organization owner"
            )

        # Get member
        query = (
            select(OrganizationMember)
            .where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id
                )
            )
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        # Remove member
        await self.db.delete(member)
        await self.db.commit()

        # Audit log
        query = (
            select(User)
            .where(User.id == user_id)
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        await self.auth_service.create_audit_log(
            action=AuditAction.delete,
            category=AuditCategory.organization_member,
            user_id=admin_id,
            details=f"Removed member {user.email if user else user_id} from {org.name}",
            request=request
        )

    async def update_member_role(
        self,
        org_id: UUID,
        user_id: UUID,
        new_role: UserRole,
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> OrganizationMember:
        """Update a member's role"""
        # Check if organization exists
        org = await self.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check admin permissions
        if not await self.is_admin(org_id, admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update member roles"
            )

        # Cannot update owner's role
        if user_id == org.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update organization owner's role"
            )

        # Get member
        query = (
            select(OrganizationMember)
            .where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id
                )
            )
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        # Update role
        member.role = new_role
        await self.db.commit()
        await self.db.refresh(member)

        # Audit log
        query = (
            select(User)
            .where(User.id == user_id)
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        await self.auth_service.create_audit_log(
            action=AuditAction.update,
            category=AuditCategory.organization_member,
            user_id=admin_id,
            details=f"Updated role for {user.email if user else user_id} in {org.name} to {new_role}",
            request=request
        )

        return member

    async def get_owned_organizations(self, user_id: UUID) -> List[Organization]:
        query = (
            select(Organization)
            .where(Organization.owner_id == user_id)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    
    async def list_members(self, org_id: UUID) -> List[dict]:
        # First get the organization to ensure it exists
        org_query = select(Organization).where(Organization.id == org_id)
        org_result = await self.db.execute(org_query)
        organization = org_result.scalar_one_or_none()
        
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Get all members with their user data
        query = (
            select(OrganizationMember)
            .options(joinedload(OrganizationMember.user))
            .where(OrganizationMember.organization_id == org_id)
        )
        result = await self.db.execute(query)
        members = list(result.scalars().all())
        
        # Convert to dictionaries to avoid async ORM issues
        member_dicts = []
        for member in members:
            # Create a basic member dict with all attributes
            member_dict = {
                "id": member.id,
                "organization_id": member.organization_id,
                "role": member.role,
                "status": member.status,
                "email": member.user.email if member.user else None,
                "first_name": member.user.first_name if member.user else None,
                "last_name": member.user.last_name if member.user else None,
                "created_at": member.created_at,
                "updated_at": member.updated_at,
                "is_verified": member.user.is_verified if member.user else False,
                "avatar_url": None  # Default value
            }
            
            # Add organization data
            member_dict["organization"] = {
                "id": organization.id,
                "name": organization.name,
                "description": organization.description,
                "status": organization.status
            }
            
            member_dicts.append(member_dict)
        
        # Load profile data for each member
        user_ids = [member.user_id for member in members if member.user_id]
        if user_ids:
            # Fetch all profiles in a single query
            profile_query = select(UserProfile).where(UserProfile.user_id.in_(user_ids))
            profile_result = await self.db.execute(profile_query)
            profiles = {profile.user_id: profile for profile in profile_result.scalars().all()}
            
            # Attach avatar_url to each member dict
            for i, member in enumerate(members):
                if member.user_id in profiles and profiles[member.user_id].avatar_url:
                    member_dicts[i]["avatar_url"] = profiles[member.user_id].avatar_url
                else:
                    # Generate a fallback avatar URL
                    full_name = f"{member.user.first_name or ''}+{member.user.last_name or ''}" if member.user else f"{member.email or ''}"
                    member_dicts[i]["avatar_url"] = f"https://ui-avatars.com/api/?name={full_name}&background=random"
        
        return member_dicts

    async def get_organization_members(
        self,
        org_id: UUID,
        user_id: UUID
    ) -> List[OrganizationMember]:
        """Get all members of an organization"""
        # Check if organization exists
        org = await self.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check if user is a member
        if not await self.is_member(org_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view members"
            )

        # Get members
        query = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == org_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def is_member(self, org_id: UUID, user_id: UUID) -> bool:
        """Check if user is a member of organization"""
        query = (
            select(OrganizationMember)
            .where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def is_admin(self, org_id: UUID, user_id: UUID) -> bool:
        """Check if user is an admin of organization"""
        query = (
            select(OrganizationMember)
            .where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id,
                    OrganizationMember.role == UserRole.admin
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def is_owner(self, org_id: UUID, user_id: UUID) -> bool:
        """Check if user is the owner of organization"""
        query = (
            select(Organization)
            .where(
                and_(
                    Organization.id == org_id,
                    Organization.owner_id == user_id
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    # --- Organization Settings Logic ---
    async def get_settings(self, org_id: UUID):
        org = await self.db.get(Organization, org_id)
        if not org:
            return None
        owner_user = await self.db.get(User, org.owner_id)
        user_profile = await self.db.execute(select(UserProfile).where(UserProfile.user_id == org.owner_id))
        user_profile = user_profile.scalar_one_or_none()
        return {
            "name": org.name,
            "description": org.description,
            "contact_email": owner_user.email if owner_user else None,
            "phone_number": user_profile.phone_number if user_profile else None,
            "avatar_url": user_profile.avatar_url if user_profile else None
        }

    async def update_settings(self, org_id: UUID, data: Dict[str, Any]):
        org = await self.db.get(Organization, org_id)
        if not org:
            return None
        owner_user = await self.db.get(User, org.owner_id)
        user_profile = await self.db.execute(select(UserProfile).where(UserProfile.user_id == org.owner_id))
        user_profile = user_profile.scalar_one_or_none()
        if data.get("name") is not None:
            org.name = data["name"]
        if data.get("description") is not None:
            org.description = data["description"]
        if data.get("contact_email") is not None and owner_user:
            owner_user.email = data["contact_email"]
        if data.get("phone_number") is not None and user_profile:
            user_profile.phone_number = data["phone_number"]
        await self.db.commit()
        await self.db.refresh(org)
        if owner_user:
            await self.db.refresh(owner_user)
        if user_profile:
            await self.db.refresh(user_profile)
        return await self.get_settings(org_id)

    async def update_avatar(self, org_id: UUID, avatar_url: str):
        org = await self.db.get(Organization, org_id)
        if not org:
            return None
        user_profile = await self.db.execute(select(UserProfile).where(UserProfile.user_id == org.owner_id))
        user_profile = user_profile.scalar_one_or_none()
        if user_profile:
            user_profile.avatar_url = avatar_url
            await self.db.commit()
            await self.db.refresh(user_profile)
        return await self.get_settings(org_id)

    async def update_member_permissions(
        self,
        org_id: UUID,
        user_id: UUID,
        permissions_data: Dict[str, Any],
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> OrganizationMember:
        """Update a member's permissions including custom permissions"""
        # Check if organization exists
        org = await self.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
            
        # Check if user is a member of organization
        query = (
            select(OrganizationMember)
            .where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id
                )
            )
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found in organization"
            )
            
        # Check if admin has permission to update member
        if not await self.is_admin(org_id, admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update member permissions"
            )
            
        # Update permissions
        standard_permissions = permissions_data.get("permissions", {})
        custom_permissions = permissions_data.get("custom_permissions", [])
        
        # Combine standard and custom permissions into a single JSONB object
        combined_permissions = standard_permissions.copy()
        
        # Add custom permissions to the combined permissions
        if custom_permissions:
            combined_permissions["custom"] = custom_permissions
            
        # Update member permissions
        member.permissions = combined_permissions
        member.updated_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(member)
        
        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.update,
            category=AuditCategory.organization,
            user_id=admin_id,
            details=f"Updated permissions for member {user_id} in organization {org_id}",
            request=request
        )
        
        return member