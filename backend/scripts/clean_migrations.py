import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection parameters
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')

# Construct database URL
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create engine
engine = create_engine(DATABASE_URL)

# Clean up alembic_version table
with engine.connect() as connection:
    try:
        connection.execute(text("DELETE FROM alembic_version;"))
        connection.commit()
        print("Successfully cleaned up alembic_version table")
    except Exception as e:
        print(f"Error cleaning up alembic_version table: {e}")
