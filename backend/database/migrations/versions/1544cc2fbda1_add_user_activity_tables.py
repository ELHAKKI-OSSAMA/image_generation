"""add user activity tables

Revision ID: 1544cc2fbda1
Revises: add_organization_indexes
Create Date: 2025-04-02 18:32:28.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB

# revision identifiers, used by Alembic.
revision = '1544cc2fbda1'
down_revision = 'add_organization_indexes'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create UserActionType enum if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_action_type') THEN
                CREATE TYPE user_action_type AS ENUM ('login', 'logout', 'password_change', 'profile_update', 'api_access', 'feature_use');
            END IF;
        END$$;
    """)
    
    # Create SessionStatus enum if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'session_status') THEN
                CREATE TYPE session_status AS ENUM ('active', 'expired', 'terminated');
            END IF;
        END$$;
    """)
    
    # Create user_sessions table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
            token VARCHAR(255) NOT NULL UNIQUE,
            refresh_token VARCHAR(255) UNIQUE,
            ip_address INET,
            user_agent TEXT,
            status session_status NOT NULL DEFAULT 'active',
            started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_activity TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at TIMESTAMPTZ NOT NULL,
            ended_at TIMESTAMPTZ
        );
    """)
    
    # Create user_actions table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_actions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
            session_id UUID REFERENCES user_sessions(id) ON DELETE SET NULL,
            action_type user_action_type NOT NULL,
            endpoint TEXT,
            method VARCHAR(10),
            ip_address INET,
            user_agent TEXT,
            status_code INTEGER,
            response_time INTEGER,
            details JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)
    
    # Create indices for better query performance if they don't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_sessions_user_id') THEN
                CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_sessions_org_id') THEN
                CREATE INDEX idx_user_sessions_org_id ON user_sessions(organization_id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_sessions_status') THEN
                CREATE INDEX idx_user_sessions_status ON user_sessions(status);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_sessions_started_at') THEN
                CREATE INDEX idx_user_sessions_started_at ON user_sessions(started_at);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_sessions_last_activity') THEN
                CREATE INDEX idx_user_sessions_last_activity ON user_sessions(last_activity);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_actions_user_id') THEN
                CREATE INDEX idx_user_actions_user_id ON user_actions(user_id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_actions_org_id') THEN
                CREATE INDEX idx_user_actions_org_id ON user_actions(organization_id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_actions_session_id') THEN
                CREATE INDEX idx_user_actions_session_id ON user_actions(session_id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_actions_action_type') THEN
                CREATE INDEX idx_user_actions_action_type ON user_actions(action_type);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'idx_user_actions_created_at') THEN
                CREATE INDEX idx_user_actions_created_at ON user_actions(created_at);
            END IF;
        END$$;
    """)

def downgrade() -> None:
    # Drop indices
    op.execute("""
        DROP INDEX IF EXISTS idx_user_actions_created_at;
        DROP INDEX IF EXISTS idx_user_actions_action_type;
        DROP INDEX IF EXISTS idx_user_actions_session_id;
        DROP INDEX IF EXISTS idx_user_actions_org_id;
        DROP INDEX IF EXISTS idx_user_actions_user_id;
        
        DROP INDEX IF EXISTS idx_user_sessions_last_activity;
        DROP INDEX IF EXISTS idx_user_sessions_started_at;
        DROP INDEX IF EXISTS idx_user_sessions_status;
        DROP INDEX IF EXISTS idx_user_sessions_org_id;
        DROP INDEX IF EXISTS idx_user_sessions_user_id;
    """)
    
    # Drop tables
    op.execute("""
        DROP TABLE IF EXISTS user_actions;
        DROP TABLE IF EXISTS user_sessions;
    """)
    
    # Drop enums
    op.execute("""
        DROP TYPE IF EXISTS user_action_type;
        DROP TYPE IF EXISTS session_status;
    """)