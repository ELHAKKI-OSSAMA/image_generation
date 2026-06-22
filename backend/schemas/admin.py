from pydantic import BaseModel, UUID4, Field
from typing import Dict, Optional, List, Any
from datetime import datetime
from models.enums import UserRole
# from schemas.organization import OrganizationResponse

class AdminBase(BaseModel):
    permissions: Dict[str, bool] = Field(
        default_factory=lambda: {
            "manage_users": False,
            "manage_organizations": False,
            "manage_admins": False,
            "view_system_stats": False,
            "manage_content": False,
            "manage_settings": False
        }
    )

class AdminCreate(AdminBase):
    user_id: UUID4

class AdminUpdate(BaseModel):
    permissions: Optional[Dict[str, bool]] = None

class AdminResponse(AdminBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    user: 'UserResponse'  # Forward reference to UserResponse

    model_config = {
    "from_attributes": True,
    "protected_namespaces": ()  # Add this line
}

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_organizations: int
    active_organizations: int
    total_admins: int
    total_events: int
    storage_usage: float  # in GB
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    registration_stats: Dict[str, int]  # date -> count
    login_stats: Dict[str, int]  # date -> count

class AuditLog(BaseModel):
    id: UUID4
    user_id: Optional[UUID4]
    action: str
    resource_type: str
    resource_id: Optional[UUID4]
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    model_config = {
    "from_attributes": True,
    "protected_namespaces": ()  # Add this line
    }

class MaintenanceStats(BaseModel):
    expired_sessions_cleaned: int
    expired_tokens_cleaned: int
    rate_limits_cleaned: int
    storage_reclaimed: float  # in MB
    execution_time: float  # in seconds

# Import at the BOTTOM
from .auth import UserResponse
AdminResponse.model_rebuild()