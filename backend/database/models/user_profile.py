from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
import uuid

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(50))
    timezone = Column(String(50), default='UTC')
    avatar_url = Column(String)
    two_factor_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, full_name={self.full_name})>"
