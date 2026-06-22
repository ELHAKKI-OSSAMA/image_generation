"""add permissions to users

Revision ID: add_permissions_to_users
Revises: add_organization_indexes
Create Date: 2025-04-01 14:02:58.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_permissions_to_users'
down_revision = 'add_organization_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Add permissions column to users table
    op.add_column('users',
        sa.Column('permissions', postgresql.JSONB, nullable=False, server_default='{}')
    )


def downgrade():
    # Remove permissions column from users table
    op.drop_column('users', 'permissions')
