"""create user profiles table

Revision ID: create_user_profiles_table
Revises: add_permissions_to_users
Create Date: 2025-04-10 15:21:44.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_user_profiles_table'
down_revision = 'add_permissions_to_users'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('phone_number', sa.String(50)),
        sa.Column('timezone', sa.String(50), server_default='UTC'),
        sa.Column('avatar_url', sa.String),
        sa.Column('two_factor_enabled', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )

    # Create index for faster lookups
    op.create_index('idx_user_profiles_user_id', 'user_profiles', ['user_id'])

def downgrade() -> None:
    # Drop index first
    op.drop_index('idx_user_profiles_user_id')
    
    # Drop the table
    op.drop_table('user_profiles')
