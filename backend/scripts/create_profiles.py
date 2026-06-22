import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import async_session

async def create_profiles_for_existing_users():
    async with async_session() as session:
        # Insert profiles for users that don't have one
        await session.execute(text("""
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
        """))
        await session.commit()
        print("Successfully created profiles for existing users")

if __name__ == "__main__":
    asyncio.run(create_profiles_for_existing_users())
