from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from aiodataloader import DataLoader
from fastapi import Depends

from core.dependencies import get_db
from models.user import Organization, OrganizationMember, User
from core.cache import CacheService

class OrganizationDataLoader:
    """DataLoader implementation for efficient organization data loading."""
    
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        cache: CacheService = Depends()
    ):
        """Initialize data loaders for different organization-related queries."""
        self.db = db
        self.cache = cache
        
        # Individual loaders for different types of queries
        self.org_loader = DataLoader(
            load_fn=self._load_organizations,
            cache=True
        )
        self.member_loader = DataLoader(
            load_fn=self._load_members,
            cache=True
        )
        self.user_orgs_loader = DataLoader(
            load_fn=self._load_user_organizations,
            cache=True
        )

    async def _load_organizations(self, ids: List[UUID]) -> List[Organization]:
        """Batch load organizations by IDs."""
        # Try cache first
        cached_orgs = {}
        missing_ids = []
        
        for org_id in ids:
            if cached := await self.cache.get_organization(org_id):
                cached_orgs[org_id] = Organization(**cached)
            else:
                missing_ids.append(org_id)
                
        if not missing_ids:
            return [cached_orgs[org_id] for org_id in ids]
            
        # Load missing from database
        stmt = (
            select(Organization)
            .options(
                selectinload(Organization.owner),
                selectinload(Organization.members)
                    .selectinload(OrganizationMember.user)
            )
            .where(Organization.id.in_(missing_ids))
        )
        result = await self.db.execute(stmt)
        orgs = result.scalars().unique().all()
        
        # Update cache
        for org in orgs:
            await self.cache.set_organization(
                org.id,
                org.to_dict(),
                expire=3600
            )
            cached_orgs[org.id] = org
            
        # Return in correct order
        return [cached_orgs.get(org_id) for org_id in ids]

    async def _load_members(
        self,
        org_ids: List[UUID]
    ) -> List[List[OrganizationMember]]:
        """Batch load members for multiple organizations."""
        stmt = (
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(OrganizationMember.organization_id.in_(org_ids))
        )
        result = await self.db.execute(stmt)
        members = result.scalars().all()
        
        # Group by organization
        grouped: Dict[UUID, List[OrganizationMember]] = {
            org_id: [] for org_id in org_ids
        }
        for member in members:
            grouped[member.organization_id].append(member)
            
        return [grouped[org_id] for org_id in org_ids]

    async def _load_user_organizations(
        self,
        user_ids: List[UUID]
    ) -> List[List[Organization]]:
        """Batch load organizations for multiple users."""
        stmt = (
            select(Organization)
            .distinct()
            .join(
                OrganizationMember,
                Organization.id == OrganizationMember.organization_id
            )
            .options(
                selectinload(Organization.owner),
                selectinload(Organization.members)
            )
            .where(
                OrganizationMember.user_id.in_(user_ids)
            )
        )
        result = await self.db.execute(stmt)
        orgs = result.scalars().unique().all()
        
        # Group by user
        grouped: Dict[UUID, List[Organization]] = {
            user_id: [] for user_id in user_ids
        }
        for org in orgs:
            for member in org.members:
                if member.user_id in user_ids:
                    grouped[member.user_id].append(org)
                    
        return [grouped[user_id] for user_id in user_ids]

    async def get_organization(self, org_id: UUID) -> Organization:
        """Get a single organization with all relations loaded."""
        return await self.org_loader.load(org_id)

    async def get_organizations(self, org_ids: List[UUID]) -> List[Organization]:
        """Get multiple organizations with all relations loaded."""
        return await self.org_loader.load_many(org_ids)

    async def get_members(self, org_id: UUID) -> List[OrganizationMember]:
        """Get all members of an organization."""
        return await self.member_loader.load(org_id)

    async def get_user_organizations(self, user_id: UUID) -> List[Organization]:
        """Get all organizations for a user."""
        return await self.user_orgs_loader.load(user_id)

    async def clear_cache(self) -> None:
        """Clear all DataLoader caches."""
        self.org_loader.clear()
        self.member_loader.clear()
        self.user_orgs_loader.clear()
