from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")

    def __repr__(self) -> str:
        return f"<PasswordResetToken {self.token} for user {self.user_id}>"
