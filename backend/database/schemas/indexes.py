"""Database indexes for optimizing query performance."""

from sqlalchemy import Index, text
from database.models.base import Base
from database.models.organization import Organization, OrganizationMember
from database.models.user import User

# Organization indexes
Index('idx_org_name', Organization.name)
Index('idx_org_status', Organization.status)
Index('idx_org_owner', Organization.owner_id)
Index('idx_org_created', Organization.created_at)
Index('idx_org_composite_owner_status', Organization.owner_id, Organization.status)

# Organization member indexes
Index('idx_org_member_user', OrganizationMember.user_id)
Index('idx_org_member_org', OrganizationMember.organization_id)
Index('idx_org_member_role', OrganizationMember.role)
Index('idx_org_member_composite', 
      OrganizationMember.organization_id, 
      OrganizationMember.user_id, 
      OrganizationMember.role)
Index('idx_org_member_permissions', 
      OrganizationMember.permissions, 
      postgresql_using='gin')

# User indexes
Index('idx_user_email', User.email)
Index('idx_user_role', User.role)
Index('idx_user_status', User.status)
Index('idx_user_composite_role_status', User.role, User.status)
