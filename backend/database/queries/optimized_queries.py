"""Optimized database queries with eager loading."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.organization import Organization, OrganizationMember
from database.models.user import User
from database.models.enums import OrganizationStatus, UserRole

class OptimizedQueries:
    """Optimized database queries with proper eager loading and joins."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_organization_with_members(
        self,
        org_id: UUID,
        load_owner: bool = True
    ) -> Optional[Organization]:
        """Get organization with eager loaded members and optionally owner."""
        query = (
            select(Organization)
            .where(Organization.id == org_id)
            .options(
                selectinload(Organization.members)
                .joinedload(OrganizationMember.user)
            )
        )
        
        if load_owner:
            query = query.options(joinedload(Organization.owner))
            
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_organizations(
        self,
        user_id: UUID,
        status: Optional[OrganizationStatus] = None
    ) -> List[Organization]:
        """Get all organizations for a user with proper eager loading."""
        query = (
            select(Organization)
            .distinct()
            .join(OrganizationMember)
            .options(
                selectinload(Organization.members)
                .joinedload(OrganizationMember.user),
                joinedload(Organization.owner)
            )
            .where(
                or_(
                    Organization.owner_id == user_id,
                    and_(
                        OrganizationMember.user_id == user_id,
                        OrganizationMember.organization_id == Organization.id
                    )
                )
            )
        )
        
        if status:
            query = query.where(Organization.status == status)
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_organization_members(
        self,
        org_id: UUID,
        role: Optional[UserRole] = None,
        include_user_data: bool = True
    ) -> List[OrganizationMember]:
        """Get organization members with optional role filter."""
        query = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == org_id)
        )
        
        if role:
            query = query.where(OrganizationMember.role == role)
            
        if include_user_data:
            query = query.options(joinedload(OrganizationMember.user))
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_organizations_batch(
        self,
        org_ids: List[UUID],
        include_members: bool = True
    ) -> Dict[UUID, Organization]:
        """Batch load multiple organizations efficiently."""
        query = (
            select(Organization)
            .where(Organization.id.in_(org_ids))
            .options(joinedload(Organization.owner))
        )
        
        if include_members:
            query = query.options(
                selectinload(Organization.members)
                .joinedload(OrganizationMember.user)
            )
            
        result = await self.db.execute(query)
        organizations = result.scalars().all()
        return {org.id: org for org in organizations}

    async def get_user_permissions_batch(
        self,
        user_id: UUID,
        org_ids: List[UUID]
    ) -> Dict[UUID, Dict[str, Any]]:
        """Batch load user permissions for multiple organizations."""
        query = (
            select(OrganizationMember)
            .where(
                and_(
                    OrganizationMember.user_id == user_id,
                    OrganizationMember.organization_id.in_(org_ids)
                )
            )
        )
        
        result = await self.db.execute(query)
        members = result.scalars().all()
        return {
            member.organization_id: {
                'role': member.role,
                'permissions': member.permissions
            }
            for member in members
        }

    async def search_organizations(
        self,
        search_term: str,
        status: Optional[OrganizationStatus] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Organization]:
        """Search organizations with efficient pagination."""
        query = (
            select(Organization)
            .where(Organization.name.ilike(f"%{search_term}%"))
            .options(
                joinedload(Organization.owner),
                selectinload(Organization.members).load_only(
                    OrganizationMember.id,
                    OrganizationMember.role
                )
            )
            .limit(limit)
            .offset(offset)
        )
        
        if status:
            query = query.where(Organization.status == status)
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_member_count(self, org_id: UUID) -> int:
        """Get organization member count efficiently."""
        query = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == org_id)
            .with_only_columns([OrganizationMember.id])
        )
        
        result = await self.db.execute(query)
        return len(result.scalars().all())
