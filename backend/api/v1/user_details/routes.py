from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from services.admin_service import AdminService
from core.database import get_db
from api.v1.auth.dependencies import get_current_user
from database.models.user import User
from schemas.user_details import (
    UserDetailsResponse,
    UserDetailsUpdate,
)

router = APIRouter()


@router.get("/user-details", response_model=UserDetailsResponse)
async def get_user_details(
    current_user: User = Depends(get_current_user),
) -> UserDetailsResponse:
    """Get the current user's details."""
    return {
        "id": current_user.id,
        "role": current_user.role,
        "permissions": current_user.permissions,
        "status": current_user.status,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }


@router.put("/user-details", response_model=UserDetailsResponse)
async def update_user_details(
    details_data: UserDetailsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserDetailsResponse:
    """Update the current user's details and sync permissions with Admin if applicable."""
    # Update user fields
    for field, value in details_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    # Sync only the 'permissions' field with Admin if it exists
    if 'permissions' in details_data.dict(exclude_unset=True):
        admin_service = AdminService(db)  # Instantiate the AdminService
        success = await admin_service.sync_permissions_with_admin(
            current_user.id, current_user.permissions
        )
        if not success:
            # Handle failure (you can log or raise an exception if needed)
            pass

    await db.commit()
    await db.refresh(current_user)

    return {
        "id": current_user.id,
        "role": current_user.role,
        "permissions": current_user.permissions,
        "status": current_user.status,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }


@router.delete("/user-details")
async def reset_user_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reset the user's details to default values and sync with admin permissions."""

    # Reset user details
    current_user.permissions = {}  # Reset to empty dict
    current_user.status = "PENDING"  # Reset to default status
    # Note: We don't reset role as it's a critical field

    # Sync the permissions reset with the Admin record if it exists
    admin_service = AdminService(db)  # Instantiate the AdminService
    success = await admin_service.sync_permissions_with_admin(
        current_user.id, current_user.permissions
    )
    if not success:
        # Handle failure if Admin record is not found or permissions can't be updated
        pass

    await db.commit()
    await db.refresh(current_user)
    
    return {"message": "User details reset successfully"}
