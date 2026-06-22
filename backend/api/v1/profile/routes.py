from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pathlib import Path
import os
import aiofiles

from core.database import get_db
from api.v1.auth.dependencies import get_current_user
from database.models import User, UserProfile
from schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    """Get the current user's profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        # Create a default profile if it doesn't exist
        profile = UserProfile(
            user_id=current_user.id,
            full_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or None
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    
    return profile

@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    """Update the current user's profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update profile fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    # Add these new lines here
    if profile_data.full_name:
        names = profile_data.full_name.split(' ', 1)
        current_user.first_name = names[0]
        current_user.last_name = names[1] if len(names) > 1 else ''
    
    await db.commit()
    await db.refresh(profile)
    return profile

@router.put("/profile/avatar")
async def update_avatar(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        print("Starting avatar upload...")
        # Get the file from form data
        form = await request.form()
        print("Form data received:", form)
        
        # Get the file from the form
        avatar = form.get("avatar")
        if not avatar:
            raise HTTPException(status_code=400, detail="No avatar file provided")
        
        # Get the content type
        content_type = getattr(avatar, 'content_type', None)
        if not content_type or not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == current_user.id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)

        # Validate content type first
        if not avatar.content_type or not avatar.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Map content type to extension
        content_type_to_extension = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
        }
        file_extension = content_type_to_extension.get(avatar.content_type)
        if not file_extension:
            raise HTTPException(status_code=400, detail="Unsupported image format")

        filename = f"{current_user.id}.{file_extension}"
        file_path = Path(f"uploads/avatars/{filename}")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await avatar.read() if hasattr(avatar, 'read') else avatar
            await f.write(content)

        # Update profile
        profile.avatar_url = f"/uploads/avatars/{filename}"
        await db.commit()
        await db.refresh(profile)
        return {"avatar_url": profile.avatar_url}

    except HTTPException as he:
        # Re-raise known exceptions
        raise he
    except Exception as e:
        print(f"Avatar upload failed with error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Avatar upload failed: {str(e)}"
        )
    finally:
        if 'avatar' in locals() and hasattr(avatar, 'seek'):
            await avatar.seek(0)  # Reset file pointer only if avatar exists and has seek method

@router.post("/profile/two-factor", response_model=ProfileResponse)
async def toggle_two_factor(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    """Toggle two-factor authentication for the current user."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    profile.two_factor_enabled = not profile.two_factor_enabled
    await db.commit()
    await db.refresh(profile)
    return profile
