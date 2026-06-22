from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from database.enums import ParticipantStatus

class EventParticipant(Base):
    __tablename__ = "event_participants"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()")
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    organization_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    event_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))  # Reference to events table
    status: Mapped[ParticipantStatus] = mapped_column(default=ParticipantStatus.REGISTERED)

    # Relationships
    user = relationship("User", back_populates="participations")
    organization = relationship("Organization", back_populates="participants")
