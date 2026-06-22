"""create profiles for existing users

Revision ID: create_profiles_for_existing_users
Revises: create_user_profiles_table
Create Date: 2025-04-10 15:32:36.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_profiles_for_existing_users'
down_revision = 'create_user_profiles_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create profiles for existing users
    op.execute("""
        INSERT INTO user_profiles (id, user_id, full_name, timezone, avatar_url, two_factor_enabled, created_at)
        SELECT 
            uuid_generate_v4(),
            u.id,
            TRIM(CONCAT(COALESCE(u.first_name, ''), ' ', COALESCE(u.last_name, ''))) as full_name,
            'UTC',
            'https://ui-avatars.com/api/?name=' || TRIM(CONCAT(COALESCE(u.first_name, ''), '+', COALESCE(u.last_name, ''))) || '&background=random',
            false,
            CURRENT_TIMESTAMP
        FROM users u
        LEFT JOIN user_profiles up ON u.id = up.user_id
        WHERE up.id IS NULL;
    """)

def downgrade() -> None:
    # Nothing to do in downgrade since we don't want to delete profiles
    pass
