from datetime import datetime
from typing import Optional, List, Dict, TYPE_CHECKING, Any
from database.models.enums import OrganizationStatus, UserRole
from pydantic import BaseModel, Field, UUID4, ConfigDict
from .base_models import BaseOrganizationResponse

if TYPE_CHECKING:
    from .auth import UserResponse
else:
    UserResponse = Any  # We'll use Any for runtime

class SimpleOrganizationResponse(BaseModel):
    id: UUID4
    name: str
    description: Optional[str] = None
    status: OrganizationStatus

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None

    model_config = {"protected_namespaces": ()}

class OrganizationCreate(OrganizationBase):
    owner_email: str
    owner_password: str = Field(..., min_length=8)
    owner_first_name: Optional[str] = None
    owner_last_name: Optional[str] = None

    model_config = {"protected_namespaces": ()}

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None

    model_config = {"protected_namespaces": ()}

class SimpleUserResponse(BaseModel):
    id: UUID4
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

class OrganizationResponse(BaseOrganizationResponse):
    owner: Optional[SimpleUserResponse] = None

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

class OrganizationMemberBase(BaseModel):
    role: UserRole = UserRole.USER
    permissions: Dict[str, bool] = {}

    model_config = {"protected_namespaces": ()}

class OrganizationMemberCreate(OrganizationMemberBase):
    user_id: UUID4

    model_config = {"protected_namespaces": ()}

class OrganizationMemberUpdate(BaseModel):
    role: Optional[UserRole] = None
    permissions: Optional[Dict[str, bool]] = None

    model_config = {"protected_namespaces": ()}

class OrganizationMemberResponse(BaseModel):
    id: UUID4
    organization_id: UUID4
    organization: Optional[SimpleOrganizationResponse] = None
    role: UserRole
    status: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_verified: bool = False
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class OrganizationInvite(BaseModel):
    email: str
    role: UserRole = UserRole.USER
    permissions: Dict[str, bool] = {}

    model_config = {"protected_namespaces": ()}

class OrganizationStats(BaseModel):
    total_members: int
    active_members: int
    pending_members: int
    total_events: int
    active_events: int

    model_config = {"protected_namespaces": ()}

class OrganizationMembershipResponse(BaseModel):
    organization: OrganizationResponse
    role: UserRole
    permissions: Dict[str, bool]
    joined_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

# --- Organization Settings Schemas ---
from pydantic import BaseModel
from typing import Optional

class OrganizationSettingsUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    contact_email: Optional[str]
    phone_number: Optional[str]

class OrganizationSettingsResponse(OrganizationSettingsUpdate):
    avatar_url: Optional[str]

from .auth import UserResponse
OrganizationResponse.model_rebuild()
OrganizationMemberResponse.model_rebuild()