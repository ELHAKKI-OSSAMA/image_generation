"""init_auth_system

Revision ID: e4969c8c1bf6
Revises: 
Create Date: 2025-03-21 15:40:38.689087

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e4969c8c1bf6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Ensure uuid-ossp extension exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Drop existing tables if they exist
    op.execute('DROP TABLE IF EXISTS audit_logs CASCADE')
    op.execute('DROP TABLE IF EXISTS rate_limits CASCADE')
    op.execute('DROP TABLE IF EXISTS sessions CASCADE')
    op.execute('DROP TABLE IF EXISTS organization_members CASCADE')
    op.execute('DROP TABLE IF EXISTS organizations CASCADE')
    op.execute('DROP TABLE IF EXISTS admins CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')

    # Drop existing enum types if they exist
    op.execute('DROP TYPE IF EXISTS participant_status CASCADE')
    op.execute('DROP TYPE IF EXISTS organization_status CASCADE')
    op.execute('DROP TYPE IF EXISTS user_status CASCADE')
    op.execute('DROP TYPE IF EXISTS user_role CASCADE')

    # Create enum types using PostgreSQL's native syntax
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'member', 'user');
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_status') THEN
                CREATE TYPE user_status AS ENUM ('pending', 'active', 'suspended', 'banned');
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'organization_status') THEN
                CREATE TYPE organization_status AS ENUM ('pending', 'active', 'suspended');
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'participant_status') THEN
                CREATE TYPE participant_status AS ENUM ('registered', 'confirmed', 'cancelled', 'attended');
            END IF;
        END $$;
    """)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('role', postgresql.ENUM('super_admin', 'admin', 'member', 'user', name='user_role', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'active', 'suspended', 'banned', name='user_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('verification_token', sa.String(255)),
        sa.Column('verification_token_expires_at', sa.DateTime(timezone=True)),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0'),
        sa.Column('last_failed_login', sa.DateTime(timezone=True)),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create admins table
    op.create_table(
        'admins',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permissions', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )

    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'active', 'suspended', name='organization_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['admins.id']),
        sa.UniqueConstraint('name')
    )

    # Create organization_members table
    op.create_table(
        'organization_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='member'),
        sa.Column('permissions', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'organization_id')
    )

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('refresh_token', sa.String(255), nullable=False),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('is_valid', sa.Boolean(), server_default='true'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token'),
        sa.UniqueConstraint('refresh_token')
    )

    # Create rate_limits table
    op.create_table(
        'rate_limits',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('window_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_attempt', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('details', sa.Text),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_status', 'users', ['status'])
    op.create_index('idx_admins_user_id', 'admins', ['user_id'])
    op.create_index('idx_organizations_owner', 'organizations', ['owner_id'])
    op.create_index('idx_organizations_status', 'organizations', ['status'])
    op.create_index('idx_org_members_user', 'organization_members', ['user_id'])
    op.create_index('idx_org_members_org', 'organization_members', ['organization_id'])
    op.create_index('idx_org_members_role', 'organization_members', ['role'])
    op.create_index('idx_sessions_user', 'sessions', ['user_id'])
    op.create_index('idx_sessions_token', 'sessions', ['token'])
    op.create_index('idx_sessions_refresh', 'sessions', ['refresh_token'])
    op.create_index('idx_sessions_expiry', 'sessions', ['expires_at'])
    op.create_index('idx_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_category', 'audit_logs', ['category'])
    op.create_index('idx_audit_logs_created', 'audit_logs', ['created_at'])
    op.create_index('idx_rate_limits_key', 'rate_limits', ['key'])
    op.create_index('idx_rate_limits_window', 'rate_limits', ['window_start'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_rate_limits_window')
    op.drop_index('idx_rate_limits_key')
    op.drop_index('idx_audit_logs_created')
    op.drop_index('idx_audit_logs_category')
    op.drop_index('idx_audit_logs_action')
    op.drop_index('idx_audit_logs_user')
    op.drop_index('idx_sessions_expiry')
    op.drop_index('idx_sessions_refresh')
    op.drop_index('idx_sessions_token')
    op.drop_index('idx_sessions_user')
    op.drop_index('idx_org_members_role')
    op.drop_index('idx_org_members_org')
    op.drop_index('idx_org_members_user')
    op.drop_index('idx_organizations_status')
    op.drop_index('idx_organizations_owner')
    op.drop_index('idx_admins_user_id')
    op.drop_index('idx_users_status')
    op.drop_index('idx_users_email')

    # Drop tables
    op.execute('DROP TABLE IF EXISTS audit_logs CASCADE')
    op.execute('DROP TABLE IF EXISTS rate_limits CASCADE')
    op.execute('DROP TABLE IF EXISTS sessions CASCADE')
    op.execute('DROP TABLE IF EXISTS organization_members CASCADE')
    op.execute('DROP TABLE IF EXISTS organizations CASCADE')
    op.execute('DROP TABLE IF EXISTS admins CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS participant_status CASCADE')
    op.execute('DROP TYPE IF EXISTS organization_status CASCADE')
    op.execute('DROP TYPE IF EXISTS user_status CASCADE')
    op.execute('DROP TYPE IF EXISTS user_role CASCADE')
