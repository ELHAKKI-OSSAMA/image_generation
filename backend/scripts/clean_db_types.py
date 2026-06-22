"""Script to clean up existing enum types in the database."""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    # Get database connection parameters
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', '')
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_name = os.getenv('POSTGRES_DB', 'ofotolab')

    # Create database URL
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # Create engine
    engine = create_engine(database_url)

    try:
        # Connect to the database
        with engine.connect() as conn:
            # Drop all existing tables that might use the enum types
            conn.execute(text('DROP TABLE IF EXISTS audit_logs CASCADE'))
            conn.execute(text('DROP TABLE IF EXISTS rate_limits CASCADE'))
            conn.execute(text('DROP TABLE IF EXISTS sessions CASCADE'))
            conn.execute(text('DROP TABLE IF EXISTS organization_members CASCADE'))
            conn.execute(text('DROP TABLE IF EXISTS organizations CASCADE'))
            conn.execute(text('DROP TABLE IF EXISTS admins CASCADE'))
            conn.execute(text('DROP TABLE IF EXISTS users CASCADE'))

            # Drop all enum types
            conn.execute(text('DROP TYPE IF EXISTS participant_status CASCADE'))
            conn.execute(text('DROP TYPE IF EXISTS organization_status CASCADE'))
            conn.execute(text('DROP TYPE IF EXISTS user_status CASCADE'))
            conn.execute(text('DROP TYPE IF EXISTS user_role CASCADE'))

            # Commit the transaction
            conn.commit()

        print("Successfully cleaned up database types and tables.")

    except Exception as e:
        print(f"Error cleaning database: {e}")

if __name__ == '__main__':
    main()
