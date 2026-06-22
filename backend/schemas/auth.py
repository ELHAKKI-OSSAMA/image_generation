from pydantic import BaseModel, EmailStr, UUID4, Field, validator, ConfigDict
from typing import Optional, Dict, List, TYPE_CHECKING, Any, Annotated
from datetime import datetime
from database.models.enums import UserRole, VerificationStatus
from .base_models import BaseUserResponse, BaseOrganizationResponse
from .organization import SimpleOrganizationResponse, OrganizationMemberResponse

if TYPE_CHECKING:
    from .organization import OrganizationResponse
else:
    OrganizationResponse = SimpleOrganizationResponse

class TokenData(BaseModel):
    user_id: UUID4
    email: str
    role: UserRole
    exp: datetime

    model_config = {"protected_namespaces": ()}

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict  # Forward reference

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)

    model_config = {"protected_namespaces": ()}

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    confirm_password: str
    role: UserRole
    # For ORGANIZATION role
    organization_name: Optional[str] = Field(None, min_length=1, max_length=255)
    organization_type: Optional[str] = None
    organization_description: Optional[str] = None
    # For MEMBER role
    organization_id: Optional[UUID4] = None
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('organization_name', 'organization_type', 'organization_description')
    def validate_organization_fields(cls, v, values):
        if values.get('role') == UserRole.ORGANIZATION and not v:
            raise ValueError(f'Field is required for organization accounts')
        return v
    
    @validator('organization_id')
    def validate_member_fields(cls, v, values):
        if values.get('role') == UserRole.MEMBER and not v:
            raise ValueError('organization_id is required for member accounts')
        return v
    
    model_config = {"protected_namespaces": ()}

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

    model_config = {"protected_namespaces": ()}

class UserResponse(BaseUserResponse):
    organizations: List[OrganizationResponse] = []
    memberships: List["OrganizationMemberResponse"] = []
    
    @property
    def all_organizations(self) -> List[OrganizationResponse]:
        """Get all organizations (owned + member of)"""
        owned_orgs = self.organizations
        member_orgs = [m.organization for m in self.memberships if m.organization]
        return owned_orgs + member_orgs
    
    model_config = {
        "from_attributes": True,
        "protected_namespaces": (),
        "json_schema_extra": {"examples": [{}]}
    }

class UserRegistrationResponse(BaseUserResponse):
    """Response model specifically for user registration endpoint"""
    model_config = {
        "from_attributes": True,
        "protected_namespaces": (),
        "json_schema_extra": {"examples": [{}]},
    }

class OrganizationOwnerResponse(BaseUserResponse):
    """Response model for organization owner registration"""
    organization: OrganizationResponse
    
    model_config = {
        "from_attributes": True,
        "protected_namespaces": (),
        "json_schema_extra": {"examples": [{}]},
    }

class OrganizationMemberResponse(BaseUserResponse):
    """Response model for organization member registration"""
    organization: OrganizationResponse
    
    model_config = {
        "from_attributes": True,
        "protected_namespaces": (),
        "json_schema_extra": {"examples": [{}]},
    }

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[VerificationStatus] = None
    is_verified: Optional[bool] = None

    model_config = {"protected_namespaces": ()}
    
class PasswordResetRequest(BaseModel):
    email: EmailStr

    model_config = {"protected_namespaces": ()}

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    model_config = {"protected_namespaces": ()}

class EmailVerification(BaseModel):
    token: str

    model_config = {"protected_namespaces": ()}

class SessionCreate(BaseModel):
    user_id: UUID4
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    remember_me: bool = False

    model_config = {"protected_namespaces": ()}

class SessionResponse(BaseModel):
    id: UUID4
    token: str
    refresh_token: str
    expires_at: datetime
    is_valid: bool
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    
    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }
    
class RegistrationResponse(BaseModel):
    # Base user fields that everyone gets
    id: UUID4
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_verified: bool
    created_at: datetime
    
    # Optional fields based on role
    organization: Optional[BaseOrganizationResponse] = None  # For MEMBER/ADMIN with org
    admin_permissions: Optional[Dict[str, List[str]]] = None  # For ADMIN/SUPER_ADMIN
    
    model_config = ConfigDict(from_attributes=True)

from .organization import OrganizationResponse
UserResponse.model_rebuild()
OrganizationOwnerResponse.model_rebuild()
OrganizationMemberResponse.model_rebuild()