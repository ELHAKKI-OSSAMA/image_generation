from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from uuid import uuid4

from database.models.base import Base

class Image(Base):
    __tablename__ = "images"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    image_base64 = Column(String, nullable=False)  # Storing base64-encoded image
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Foreign keys (without relationships)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    event_id = Column(PGUUID(as_uuid=True), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    guest_id = Column(PGUUID(as_uuid=True), ForeignKey("guests.id", ondelete="SET NULL"), nullable=True)