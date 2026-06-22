"""create permission tables

Revision ID: create_permission_tables
Revises: 
Create Date: 2025-03-30 16:12:26.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_permission_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('role', 'permission_id', name='unique_role_permission')
    )

    # Create user_permissions table
    op.create_table(
        'user_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True)),
        sa.Column('granted_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('user_id', 'permission_id', 'organization_id', name='unique_user_permission')
    )

    # Create indexes
    op.create_index('idx_permissions_name', 'permissions', ['name'])
    op.create_index('idx_role_permissions_role', 'role_permissions', ['role'])
    op.create_index('idx_user_permissions_user', 'user_permissions', ['user_id'])
    op.create_index('idx_user_permissions_org', 'user_permissions', ['organization_id'])
    op.create_index('idx_user_permissions_active', 'user_permissions', ['is_active'])

def downgrade():
    op.drop_table('user_permissions')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
