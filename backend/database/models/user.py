from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from sqlalchemy import String, Boolean, Integer, DateTime, Enum, ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.enums import UserRole, VerificationStatus
from common.constants.permissions import DEFAULT_ROLE_PERMISSIONS

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, create_constraint=True, native_enum=True), nullable=False)
    permissions: Mapped[Dict] = mapped_column(JSONB, nullable=False, default=lambda: DEFAULT_ROLE_PERMISSIONS["USER"])
    status: Mapped[VerificationStatus] = mapped_column(Enum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255))
    verification_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_failed_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    admin = relationship("Admin", back_populates="user", uselist=False)
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    organizations = relationship("Organization", back_populates="owner")
    memberships = relationship("OrganizationMember", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    events = relationship("Event", back_populates="user")
    verifications = relationship("Verification", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user")
    guests = relationship("Guest", back_populates="user")
    user_tokens = relationship("UserToken", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def has_admin_access(self) -> bool:
        """Check if user has admin access."""
        return self.permissions.get("all", False) or (
            self.permissions.get("manage_users", False) and 
            self.permissions.get("manage_organizations", False)
        )

    @property
    def has_super_admin_access(self) -> bool:
        """Check if user has super admin access."""
        return self.permissions.get("all", False)

    @property
    def has_organization_admin_access(self) -> bool:
        """Check if user has organization admin access."""
        return self.permissions.get("manage_org_members", False) and self.permissions.get("manage_org_settings", False)
