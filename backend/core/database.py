from typing import AsyncGenerator
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.models import admin
from database.models.base import Base
from database.config import settings
import logging
from dotenv import load_dotenv
import os

from sqlalchemy.pool import NullPool
import json
from database.models import Event,Permission,SdModelVersion, SdModel, TypeControl, ControlModel, ControlModule, ControlNet, SamplerModeTable, SamplerTypeTable, ModelCategoryTable, Model, sdmodelversion_typecontrol_association, model_controlnet_association
from datetime import datetime

load_dotenv()

DATABASE_URL = settings.get_database_url()
# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DB_ECHO_LOG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    connect_args={"port": int(os.getenv('POSTGRES_PORT'))}
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """
    Dependency generator for obtaining a database session.
    For example, can be used with FastAPI endpoints.
    """
    async with async_session() as session:
        yield session

DEFAULT_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.DB_PORT}/postgres"


async def create_database_if_not_exists():
    """
    Connects to the default 'postgres' database and creates the target database
    if it does not exist.
    """
    # Create a temporary engine connected to 'postgres' database
    engine_default = create_async_engine(
        DEFAULT_DATABASE_URL,
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT"  # Set isolation level at engine creation
    )
    
    try:
        async with engine_default.connect() as conn:
            # Check if the database exists
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'")
            )
            database_exists = result.scalar() is not None

            if not database_exists:
                logging.info(f"Database '{settings.POSTGRES_DB}' does not exist. Creating...")
                await conn.execute(text(f'CREATE DATABASE "{settings.POSTGRES_DB}"'))
                logging.info(f"Database '{settings.POSTGRES_DB}' has been created.")

            else:
                logging.info(f"Database '{settings.POSTGRES_DB}' already exists.")
    finally:
        await engine_default.dispose()

async def init_db():
    """Initialize database by creating tables."""
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        #logging.info("All tables dropped successfully")
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Tables recreated successfully")
    await jsonfiledatatest()
    await permissiondatatest()


async def permissiondatatest():
    async with async_session() as session:
        async def any_table_has_data():
            tables = [
               Permission
            ]
            for table in tables:
                result = await session.execute(select(table))
                if result.scalars().first() is not None:
                    return True  # If any table has data, return True
            return False
        # Check if data already exists
        if await any_table_has_data():
            print("Database already contains data. Skipping seeding.")
            return
        # Read the JSON file (synchronously, since file I/O is usually fast for seed files)
        with open("database/data/default_permissions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        # Insert data into tables using your ORM models.
        for permission in data.get("permission", []):
            session.add(Permission(**permission))
        await session.commit()  # Commit the main inserts
        # Insert association data (using SQLAlchemy’s Core insert syntax)
        logging.info("Default permissions seeded successfully")


async def eventdatatest():
    async with async_session() as session:
        async def any_table_has_data():
            tables = [Event]
            for table in tables:
                result = await session.execute(select(table))
                if result.scalars().first() is not None:
                    return True  # If any table has data, return True
            return False

        # Check if data already exists
        if await any_table_has_data():
            logging.info("Database already contains data. Skipping seeding.")
            return

        # Read the JSON file safely
        try:
            with open("database/data/default_event.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logging.error("Default event data file not found.")
            return
        except json.JSONDecodeError:
            logging.error("Error decoding JSON data.")
            return

        events = data.get("event", []) if isinstance(data, dict) else data  # Ensure correct structure

        # Convert event time fields from string to datetime
        for event in events:
            event["event_time"] = datetime.fromisoformat(event["event_time"])
            event["event_end_timed"] = datetime.fromisoformat(event["event_end_timed"])

            session.add(Event(**event))

        await session.commit()  # Commit the inserts
        logging.info("Default events seeded successfully")

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, admin
from database.models.enums import VerificationStatus, UserRole
from core.security import get_password_hash
from common.constants.permissions import DEFAULT_ROLE_PERMISSIONS
from uuid import uuid4
from datetime import datetime
from database.models import Plan


async def craete_default_plan(db: AsyncSession):
    async def any_table_has_data():
        tables = [Plan]
        for table in tables:
            result = await db.execute(select(table))  # ← FIXED
            if result.scalars().first() is not None:
                return True
        return False

    if await any_table_has_data():
        logging.info("Database already contains data. Skipping seeding.")
        return

    try:
        with open("database/data/default_plan.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error("Default plan data file not found.")
        return
    except json.JSONDecodeError:
        logging.error("Error decoding JSON data.")
        return

    plans = data.get("plan", []) if isinstance(data, dict) else data

    for plan in plans:
        try:
            db.add(Plan(
                id=uuid4(),
                model_list=plan.get("model_list") if plan.get("model_list") else None,
                price=plan["price"] if plan.get("price") else None,
                description=plan.get("description") if plan.get("description") else None,
                user_type=UserRole(plan["user_type"]) if plan.get("user_type") else None,
                limite_image=plan.get("image_limit") if plan.get("image_limit") else None,
                stockage=plan.get("stockage") if plan.get("stockage") else None,
                time_limit=plan.get("time_limit") if plan.get("time_limit") else None,
            ))
        except Exception as e:
            logging.error(f"Failed to create plan: {e}")

    await db.commit()
    logging.info("✅ Default plans seeded successfully.")




async def create_default_super_admin_directly(db: AsyncSession):
    email = "iaphotoshot_admin@gmail.com"

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        print("User already exists.")
        return

    new_user = User(
        id=uuid4(),
        email=email,
        password_hash=get_password_hash("123456aA@123456aA@"),
        first_name="Admin",
        last_name="Admin",
        role=UserRole.SUPER_ADMIN,
        permissions=DEFAULT_ROLE_PERMISSIONS["SUPER_ADMIN"],
        status=VerificationStatus.VERIFIED,
        is_verified=True,
        verification_token=None,
        verification_token_expires_at=None,
        failed_login_attempts=0,
        last_failed_login=None,
        last_login=datetime.utcnow(),
    )
    new_superuser = admin.Admin(
        id=uuid4(),
        user_id=new_user.id,
        role=UserRole.SUPER_ADMIN,
        permissions=DEFAULT_ROLE_PERMISSIONS["SUPER_ADMIN"]
    )

    db.add(new_user)
    db.add(new_superuser)

    await db.commit()
    print("✅ Default user created directly.")


async def jsonfiledatatest():
    
    async with async_session() as session:
        async def any_table_has_data():
            tables = [
                SdModelVersion, SdModel, TypeControl, ControlModel, ControlModule,
                ControlNet, SamplerModeTable, SamplerTypeTable, ModelCategoryTable, Model
            ]
            for table in tables:
                result = await session.execute(select(table))
                if result.scalars().first() is not None:
                    return True  # If any table has data, return True
            return False

        # Check if data already exists
        if await any_table_has_data():
            print("Database already contains data. Skipping seeding.")
            return
        
        # Read the JSON file (synchronously, since file I/O is usually fast for seed files)
        with open("database/data/init_model.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Insert data into tables using your ORM models.
        for version in data.get("sdmodel_versions", []):
            session.add(SdModelVersion(**version))
        for sdmodel in data.get("sdmodels", []):
            session.add(SdModel(**sdmodel))
        for typecontrol in data.get("typecontrols", []):
            session.add(TypeControl(**typecontrol))
        for controlmodel in data.get("controlmodels", []):
            session.add(ControlModel(**controlmodel))
        for controlmodule in data.get("controlmodules", []):
            session.add(ControlModule(**controlmodule))
        for controlnet in data.get("controlnet", []):
            session.add(ControlNet(**controlnet))
        for sampler_mode in data.get("samplermodes", []):
            session.add(SamplerModeTable(**sampler_mode))
        for sampler_type in data.get("samplertypes", []):
            session.add(SamplerTypeTable(**sampler_type))
        for model_category in data.get("category", []):
            session.add(ModelCategoryTable(**model_category))
        for model in data.get("models", []):
            session.add(Model(**model))

        await session.commit()  # Commit the main inserts

        # Insert association data (using SQLAlchemy’s Core insert syntax)
        for association in data.get("sdmodelversion_typecontrol_association", []):
            await session.execute(
                sdmodelversion_typecontrol_association.insert().values(**association)
            )
        for association in data.get("model_controlnet_association", []):
            await session.execute(
                model_controlnet_association.insert().values(**association)
            )
        await session.commit()
        print("Data seeded successfully.")

__all__ = ["engine", "async_session", "get_db", "create_tables", "init_db", "Base"]
