from uuid import UUID
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from datetime import datetime

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()")
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    organization_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    last_login: Mapped[datetime] = mapped_column(nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="members")
