from typing import Optional, List
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

# from .organization import OrganizationResponse
from database.models.enums import UserRole, VerificationStatus

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    status: Optional[VerificationStatus] = None  # Make optional
    is_verified: Optional[bool] = None  # Make optional


class UserCreate(UserBase):
    password: str
    # For ORGANIZATION role
    organization_name: Optional[str] = None
    organization_description: Optional[str] = None
    # For MEMBER role
    organization_id: Optional[UUID] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[VerificationStatus] = None
    is_verified: Optional[bool] = None

# class UserResponse(UserBase):
#     id: UUID
#     created_at: datetime
#     updated_at: datetime
#     organizations: List["OrganizationResponse"] = []

#     model_config = {  # Replace "Config" class with this
#         "from_attributes": True
#     }
class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    organizations: List["OrganizationResponse"] = []

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True  # Add this
    }
# Import at the VERY BOTTOM
from .organization import OrganizationResponse
# UserResponse.model_rebuild()