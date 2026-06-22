from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, DateTime, Enum, ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.enums import VerificationStatus, SubscriptionTier, SubscriptionStatus, UserRole, OrganizationStatus
from pydantic import BaseModel, UUID4, Field, ConfigDict

class OrganizationBase(BaseModel):
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    business_type: Optional[str] = None
    business_description: Optional[str] = None
    model_config = ConfigDict(protected_namespaces=())

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: UUID4
    status: OrganizationStatus
    subscription_tier: SubscriptionTier
    subscription_status: SubscriptionStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String)
    owner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[OrganizationStatus] = mapped_column(Enum(OrganizationStatus), nullable=False, default=OrganizationStatus.PENDING)
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.TRIAL)
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    subscription_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    subscription_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="organizations")
    approver = relationship("Admin", foreign_keys=[approved_by], back_populates="approved_organizations")
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    usage_statistics = relationship("UsageStatistic", back_populates="organization")
    events = relationship("Event", back_populates="organization")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('name', name='unique_org_name'),
    )

class OrganizationMemberBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.USER
    model_config = ConfigDict(protected_namespaces=())

class OrganizationMemberCreate(OrganizationMemberBase):
    organization_id: UUID4
    password: str

class OrganizationMemberResponse(OrganizationMemberBase):
    id: UUID4
    organization_id: UUID4
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.USER)
    permissions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    firebase_uid: Mapped[Optional[str]] = mapped_column(String(255), unique=True)

    # Relationships
    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="members")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='unique_user_organization'),
    )