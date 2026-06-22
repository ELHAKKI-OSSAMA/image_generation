from typing import Optional
from pydantic import BaseModel, constr
from datetime import datetime
from uuid import UUID

class ProfileBase(BaseModel):
    """Base schema for user profile data."""
    full_name: Optional[str] = None
    phone_number: Optional[constr(max_length=50)] = None  # type: ignore
    timezone: str = 'UTC'
    two_factor_enabled: bool = False

class ProfileCreate(ProfileBase):
    """Schema for creating a new profile."""
    user_id: UUID

class ProfileUpdate(ProfileBase):
    """Schema for updating an existing profile."""
    pass

class ProfileResponse(ProfileBase):
    """Schema for profile responses."""
    id: UUID
    user_id: UUID
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AvatarUpdate(BaseModel):
    """Schema for avatar URL updates."""
    avatar_url: str
