from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from datetime import datetime
from contextlib import asynccontextmanager
import aioredis
import logging
from typing import AsyncGenerator
from core.redis import init_redis, redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Configure CORS
import ast
# Import our new routes
from api.v1.auth.routes import router as auth_router
from api.v1.organization.routes import router as org_router
from api.v1.admin.routes import router as admin_router
from api.v1.profile.routes import router as profile_router
from api.v1.user_details.routes import router as user_details_router
from api.v1.organization import settings as organization_settings_router

# Import existing routes we want to keep
from routers.model import router as model_router
from routers.payload_model import router as payload_router
from routers.logs import router as logs_router
from routers.permission import router as permission_router
from routers.event import router as event_router
from routers.organization import router as organization_router
from routers.guest import router as guest_router
from routers.plans_subsciprtion import router as plans_subscription_router
from routers.payment_gateway import router as payment_gateway_router


from routers.image import router as image_router


# Import the new image service router
from services.image_service.main import router as image_service_router

# Import middleware and services
from middleware.rate_limiter import RateLimitMiddleware
from middleware.usage_tracking import UsageTracker
from services.auth_service import AuthService
from core.database import async_session,get_db, create_default_super_admin_directly,craete_default_plan, init_db, create_database_if_not_exists
from core.redis import get_redis

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await create_database_if_not_exists()
    await init_db()

    # Create default admin user
    async with async_session() as db:
        await create_default_super_admin_directly(db)
        await craete_default_plan(db)

    # Initialize Redis connection (optional for development)
    try:
        redis_client = await init_redis()
        if redis_client:
            await redis_client.ping()
            logger.info("✅ Successfully connected to Redis")
        else:
            logger.warning("⚠️  Redis not available - initialization failed")
            if os.getenv("ENV") == "production":
                logger.error("❌ Redis is required in production")
                raise RuntimeError("Redis is required in production")
            logger.warning("⚠️  Running without Redis - some features may be limited")
    except Exception as e:
        logger.error(f"❌ Redis connection error: {e}")
        if os.getenv("ENV") == "production":
            raise
    
    # Store Redis client in app state
    app.state.redis = redis_client
    logger.info("🚀 Redis client initialized and stored in app state")
    
    try:
        # Yield control back to FastAPI
        yield
    finally:
        # Cleanup on shutdown
        if redis_client:
            logger.info("🛑 Closing Redis connection...")
            await redis_client.close()
        logger.info("✅ Redis connection closed")

import logging
# Configure logging for the entire app
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture detailed logs
logger = logging.getLogger(__name__)      # Use __name__ for module-specific logs

# Initialize FastAPI app
app = FastAPI(
    title="Ofotolab API",
    description="API for Ofotolab image generation platform with PostgreSQL authentication",
    version="2.0.0",
    lifespan=lifespan,
)




# Convert the string list from env into a real Python list
ALLOWED_HOSTS = ast.literal_eval(os.getenv("ALLOWED_HOSTS", "[]"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,  # Correctly passing list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add usage tracking middleware
app.add_middleware(UsageTracker)
# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Mount static files directory for avatars
uploads_dir = os.path.join(os.getcwd(), "uploads")
os.makedirs(os.path.join(uploads_dir, "avatars"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(org_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(model_router, prefix="/api/v1")
app.include_router(payload_router, prefix="/api/v1")
app.include_router(logs_router, prefix="/api/v1")
app.include_router(user_details_router, prefix="/api/v1")
app.include_router(permission_router, prefix="/api/v1")
app.include_router(event_router, prefix="/api/v1")
app.include_router(organization_router, prefix="/api/v1")
app.include_router(organization_settings_router.router, prefix="/api/v1")
app.include_router(image_router, prefix="/api/v1")
app.include_router(guest_router, prefix="/api/v1")
app.include_router(plans_subscription_router, prefix="/api/v1")
app.include_router(payment_gateway_router, prefix="/api/v1")

# Notice the image service router is added with prefix /api/images
app.include_router(image_service_router, prefix="/api/v1/images")

# @app.on_event("startup")
# async def startup_event():
#     """Initialize database and run migrations"""
#     await init_db()

@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "Welcome to Ofotolab API",
            "version": "2.0.0",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        content={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
