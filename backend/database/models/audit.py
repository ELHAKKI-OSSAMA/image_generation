from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict
from sqlalchemy import String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[str] = mapped_column(String, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    event_data: Mapped[Dict] = mapped_column(JSON, nullable=False, server_default="{}")

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by user {self.user_id}>"

class RateLimit(Base):
    __tablename__ = "rate_limits"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    counter: Mapped[int] = mapped_column(nullable=False, default=1)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))