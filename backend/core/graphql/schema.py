import graphene
from typing import Any, Dict, List, Optional
from uuid import UUID

from core.data_loader import OrganizationDataLoader
from core.cache import CacheService
from models.enums import OrganizationStatus, UserRole
from .types import (
    OrganizationType,
    UserType,
    OrganizationMemberType,
    UUIDScalar
)

class Query(graphene.ObjectType):
    """Root query type."""
    
    # Organization queries
    organization = graphene.Field(
        OrganizationType,
        id=UUIDScalar(required=True)
    )
    organizations = graphene.List(
        OrganizationType,
        status=graphene.String(),
        limit=graphene.Int(),
        offset=graphene.Int()
    )
    
    # User queries
    user = graphene.Field(
        UserType,
        id=UUIDScalar(required=True)
    )
    users = graphene.List(
        UserType,
        role=graphene.String(),
        limit=graphene.Int(),
        offset=graphene.Int()
    )
    
    # Organization member queries
    organization_member = graphene.Field(
        OrganizationMemberType,
        id=UUIDScalar(required=True)
    )
    organization_members = graphene.List(
        OrganizationMemberType,
        organization_id=UUIDScalar(required=True),
        role=graphene.String(),
        limit=graphene.Int(),
        offset=graphene.Int()
    )
    
    async def resolve_organization(
        self,
        info,
        id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Resolve single organization by ID."""
        loader = info.context["organization_loader"]
        return await loader.get_organization(id)
    
    async def resolve_organizations(
        self,
        info,
        status: Optional[str] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """Resolve organizations with optional filtering."""
        loader = info.context["organization_loader"]
        return await loader.get_organizations(
            status=OrganizationStatus(status) if status else None,
            limit=limit,
            offset=offset
        )
    
    async def resolve_user(
        self,
        info,
        id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Resolve single user by ID."""
        loader = info.context["organization_loader"]
        return await loader.get_user(id)
    
    async def resolve_users(
        self,
        info,
        role: Optional[str] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """Resolve users with optional filtering."""
        loader = info.context["organization_loader"]
        return await loader.get_users(
            role=UserRole(role) if role else None,
            limit=limit,
            offset=offset
        )
    
    async def resolve_organization_member(
        self,
        info,
        id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Resolve single organization member by ID."""
        loader = info.context["organization_loader"]
        return await loader.get_member(id)
    
    async def resolve_organization_members(
        self,
        info,
        organization_id: UUID,
        role: Optional[str] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """Resolve organization members with optional filtering."""
        loader = info.context["organization_loader"]
        return await loader.get_members(
            organization_id,
            role=UserRole(role) if role else None,
            limit=limit,
            offset=offset
        )

class CreateOrganizationInput(graphene.InputObjectType):
    """Input type for creating an organization."""
    name = graphene.String(required=True)
    description = graphene.String()

class UpdateOrganizationInput(graphene.InputObjectType):
    """Input type for updating an organization."""
    name = graphene.String()
    description = graphene.String()
    status = graphene.String()

class AddOrganizationMemberInput(graphene.InputObjectType):
    """Input type for adding an organization member."""
    user_id = UUIDScalar(required=True)
    role = graphene.String(required=True)
    permissions = graphene.JSONString()

class UpdateOrganizationMemberInput(graphene.InputObjectType):
    """Input type for updating an organization member."""
    role = graphene.String()
    permissions = graphene.JSONString()

class Mutation(graphene.ObjectType):
    """Root mutation type."""
    
    # Organization mutations
    create_organization = graphene.Field(
        OrganizationType,
        input=CreateOrganizationInput(required=True)
    )
    update_organization = graphene.Field(
        OrganizationType,
        id=UUIDScalar(required=True),
        input=UpdateOrganizationInput(required=True)
    )
    delete_organization = graphene.Field(
        graphene.Boolean,
        id=UUIDScalar(required=True)
    )
    
    # Organization member mutations
    add_organization_member = graphene.Field(
        OrganizationMemberType,
        organization_id=UUIDScalar(required=True),
        input=AddOrganizationMemberInput(required=True)
    )
    update_organization_member = graphene.Field(
        OrganizationMemberType,
        id=UUIDScalar(required=True),
        input=UpdateOrganizationMemberInput(required=True)
    )
    remove_organization_member = graphene.Field(
        graphene.Boolean,
        id=UUIDScalar(required=True)
    )
    
    async def resolve_create_organization(
        self,
        info,
        input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new organization."""
        loader = info.context["organization_loader"]
        return await loader.create_organization(input)
    
    async def resolve_update_organization(
        self,
        info,
        id: UUID,
        input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing organization."""
        loader = info.context["organization_loader"]
        return await loader.update_organization(id, input)
    
    async def resolve_delete_organization(
        self,
        info,
        id: UUID
    ) -> bool:
        """Delete an organization."""
        loader = info.context["organization_loader"]
        return await loader.delete_organization(id)
    
    async def resolve_add_organization_member(
        self,
        info,
        organization_id: UUID,
        input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a member to an organization."""
        loader = info.context["organization_loader"]
        return await loader.add_member(organization_id, input)
    
    async def resolve_update_organization_member(
        self,
        info,
        id: UUID,
        input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an organization member."""
        loader = info.context["organization_loader"]
        return await loader.update_member(id, input)
    
    async def resolve_remove_organization_member(
        self,
        info,
        id: UUID
    ) -> bool:
        """Remove a member from an organization."""
        loader = info.context["organization_loader"]
        return await loader.remove_member(id)

schema = graphene.Schema(query=Query, mutation=Mutation)
