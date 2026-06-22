import graphene
from graphene import relay
from uuid import UUID
from typing import Any, Dict, List

from models.enums import OrganizationStatus, UserRole

class UUIDScalar(graphene.Scalar):
    """UUID scalar type."""

    @staticmethod
    def serialize(uuid: UUID) -> str:
        return str(uuid)

    @staticmethod
    def parse_literal(ast: Any) -> UUID:
        if isinstance(ast, graphene.StringValue):
            return UUID(ast.value)
        return None

    @staticmethod
    def parse_value(value: str) -> UUID:
        return UUID(value)

class UserType(graphene.ObjectType):
    """GraphQL type for User model."""
    
    class Meta:
        interfaces = (relay.Node,)
        
    id = UUIDScalar(required=True)
    email = graphene.String(required=True)
    first_name = graphene.String()
    last_name = graphene.String()
    role = graphene.String(required=True)
    is_verified = graphene.Boolean(required=True)
    created_at = graphene.DateTime(required=True)
    updated_at = graphene.DateTime(required=True)
    
    owned_organizations = graphene.List(lambda: OrganizationType)
    member_organizations = graphene.List(lambda: OrganizationType)

class OrganizationMemberType(graphene.ObjectType):
    """GraphQL type for OrganizationMember model."""
    
    class Meta:
        interfaces = (relay.Node,)
        
    id = UUIDScalar(required=True)
    user = graphene.Field(UserType, required=True)
    organization = graphene.Field(lambda: OrganizationType, required=True)
    role = graphene.String(required=True)
    permissions = graphene.JSONString()
    created_at = graphene.DateTime(required=True)
    updated_at = graphene.DateTime(required=True)

class OrganizationType(graphene.ObjectType):
    """GraphQL type for Organization model."""
    
    class Meta:
        interfaces = (relay.Node,)
        
    id = UUIDScalar(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    owner = graphene.Field(UserType, required=True)
    status = graphene.String(required=True)
    approved_by = graphene.Field(UserType)
    approved_at = graphene.DateTime()
    subscription_tier = graphene.String()
    member_limit = graphene.Int()
    created_at = graphene.DateTime(required=True)
    updated_at = graphene.DateTime(required=True)
    
    members = graphene.List(OrganizationMemberType)
    member_count = graphene.Int()
    
    async def resolve_members(self, info) -> List[Dict[str, Any]]:
        """Resolve organization members using DataLoader."""
        loader = info.context["organization_loader"]
        return await loader.get_members(self.id)
        
    async def resolve_member_count(self, info) -> int:
        """Resolve member count."""
        members = await self.resolve_members(info)
        return len(members)
