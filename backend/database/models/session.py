from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Boolean, DateTime, ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String)
    user_agent: Mapped[Optional[str]] = mapped_column(String)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    # Constraints
    __table_args__ = (
        UniqueConstraint('token', name='unique_session_token'),
        UniqueConstraint('refresh_token', name='unique_refresh_token'),
        {'comment': 'User sessions for authentication and token management'}
    )

    def is_expired(self) -> bool:
        """Check if the session has expired"""
        return datetime.utcnow() > self.expires_at

    def is_active(self) -> bool:
        """Check if the session is active (valid and not expired)"""
        return self.is_valid and not self.is_expired()

    def __repr__(self) -> str:
        return f"<Session {self.id} for user {self.user_id}>"
