from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime, timedelta
from uuid import uuid4

from database.models.base import Base
from database.models.enums import VerificationStatus


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(6), nullable=False)  # 6-digit verification code
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(minutes=15))
    verified_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="verifications")

    def __repr__(self):
        return f"<Verification(id={self.id}, user_id={self.user_id}, status={self.status})>"

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @property
    def is_verified(self) -> bool:
        return self.status == VerificationStatus.VERIFIED
