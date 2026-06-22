from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List, Dict
from database.models.enums import UserRole, VerificationStatus, OrganizationStatus

class BaseResponse(BaseModel):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

class BaseUserResponse(BaseResponse):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    status: VerificationStatus
    is_verified: bool
    last_login: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

class BaseOrganizationResponse(BaseResponse):
    name: str
    description: Optional[str] = None
    owner_id: UUID4
    status: OrganizationStatus
    approved_by: Optional[UUID4] = None
    approved_at: Optional[datetime] = None
    member_count: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }