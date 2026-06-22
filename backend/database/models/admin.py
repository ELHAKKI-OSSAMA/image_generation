from pydantic import BaseModel, UUID4, Field, ConfigDict
from typing import Dict, Optional, List, Any
from datetime import datetime
from sqlalchemy import Column, String, UUID, ForeignKey, TIMESTAMP, Boolean, JSON, text, Enum, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from database.models.base import Base
from database.models.enums import UserRole
import uuid
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base

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
    class Config:
        protected_namespaces = ()

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
    class Config:
        from_attributes = True
        protected_namespaces = ()

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
    class Config:
        from_attributes = True
        protected_namespaces = ()

class MaintenanceStats(BaseModel):
    expired_sessions_cleaned: int
    expired_tokens_cleaned: int
    rate_limits_cleaned: int
    storage_reclaimed: float  # in MB
    execution_time: float  # in seconds

# Import at the BOTTOM
from schemas.auth import UserResponse
AdminResponse.model_rebuild()

# SQLAlchemy Model
from uuid import UUID

from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.enums import UserRole

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.ADMIN)
    permissions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    user = relationship("User", back_populates="admin")
    approved_organizations = relationship("Organization", back_populates="approver", foreign_keys="Organization.approved_by")

    def __repr__(self):
        return f"<Admin {self.user_id}>"