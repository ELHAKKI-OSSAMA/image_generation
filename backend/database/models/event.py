from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from uuid import uuid4

from database.models.base import Base
from database.models.enums import EventType
from sqlalchemy import Enum


class Event(Base):
    __tablename__ = "events"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_end_timed = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=True)
    public = Column(Boolean, default=False)
    type=Column(Enum(EventType), nullable=True)
    location=Column(String, nullable=True)
    attendees=Column(Integer, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="events")
    user = relationship("User", back_populates="events")
    guests = relationship(
    "Guest",
    primaryjoin="Event.id == foreign(Guest.event_id)",
    viewonly=True  # ou sans viewonly si tu veux pouvoir y accéder en écriture
    )


    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', organization_id={self.organization_id})>"