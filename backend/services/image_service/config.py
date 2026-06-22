# config.py
import os
from databases import Database
import sqlalchemy
from sqlalchemy_utils import database_exists, create_database

from dotenv import load_dotenv
import os

load_dotenv()

# Read the DATABASE_URL from the environment variable, defaulting to the Docker
# expected value if not provided.
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

# Check if database exists, and if not, create it (caution: this is ideal for development)
if not database_exists(DATABASE_URL):
    create_database(DATABASE_URL)

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Define the table
images = sqlalchemy.Table(
    "images",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("model_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("source_image", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("generated_image", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("timestamp", sqlalchemy.TIMESTAMP, server_default=sqlalchemy.func.now()),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
