from fastapi import APIRouter
from api.v1.endpoints import auth, users, organizations, profile
from api.v1.user_details.routes import router as user_details_router
from api.v1.organization import settings as organization_settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(user_details_router, tags=["user-details"])
api_router.include_router(organization_settings.router)
