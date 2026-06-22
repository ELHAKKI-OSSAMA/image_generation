from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel

from database.models.user import UserRole, VerificationStatus


class UserDetailsBase(BaseModel):
    """Base schema for user details."""
    role: Optional[UserRole] = None
    permissions: Optional[Dict] = None
    status: Optional[VerificationStatus] = None


class UserDetailsCreate(UserDetailsBase):
    """Schema for creating user details."""
    pass


class UserDetailsUpdate(UserDetailsBase):
    """Schema for updating user details."""
    pass


class UserDetailsResponse(UserDetailsBase):
    """Schema for user details responses."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True