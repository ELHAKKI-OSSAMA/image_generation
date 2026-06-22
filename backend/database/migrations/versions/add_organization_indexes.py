"""Add organization optimization indexes

Revision ID: add_organization_indexes
Revises: 
Create Date: 2025-03-29 12:04:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic
revision = 'add_organization_indexes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Organization indexes
    op.create_index('idx_org_name', 'organizations', ['name'])
    op.create_index('idx_org_status', 'organizations', ['status'])
    op.create_index('idx_org_owner', 'organizations', ['owner_id'])
    op.create_index('idx_org_created', 'organizations', ['created_at'])
    op.create_index('idx_org_composite_owner_status', 'organizations', ['owner_id', 'status'])

    # Organization member indexes
    op.create_index('idx_org_member_user', 'organization_members', ['user_id'])
    op.create_index('idx_org_member_org', 'organization_members', ['organization_id'])
    op.create_index('idx_org_member_role', 'organization_members', ['role'])
    op.create_index('idx_org_member_composite', 'organization_members', 
                    ['organization_id', 'user_id', 'role'])
    
    # GIN index for JSONB permissions
    op.execute(
        'CREATE INDEX idx_org_member_permissions ON organization_members '
        'USING gin (permissions jsonb_path_ops)'
    )

    # User indexes
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_role', 'users', ['role'])
    op.create_index('idx_user_status', 'users', ['status'])
    op.create_index('idx_user_composite_role_status', 'users', ['role', 'status'])

def downgrade() -> None:
    # Drop organization indexes
    op.drop_index('idx_org_name', table_name='organizations')
    op.drop_index('idx_org_status', table_name='organizations')
    op.drop_index('idx_org_owner', table_name='organizations')
    op.drop_index('idx_org_created', table_name='organizations')
    op.drop_index('idx_org_composite_owner_status', table_name='organizations')

    # Drop organization member indexes
    op.drop_index('idx_org_member_user', table_name='organization_members')
    op.drop_index('idx_org_member_org', table_name='organization_members')
    op.drop_index('idx_org_member_role', table_name='organization_members')
    op.drop_index('idx_org_member_composite', table_name='organization_members')
    op.drop_index('idx_org_member_permissions', table_name='organization_members')

    # Drop user indexes
    op.drop_index('idx_user_email', table_name='users')
    op.drop_index('idx_user_role', table_name='users')
    op.drop_index('idx_user_status', table_name='users')
    op.drop_index('idx_user_composite_role_status', table_name='users')
