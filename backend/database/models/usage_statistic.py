from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from uuid import uuid4

from database.models.base import Base


class UsageStatistic(Base):
    __tablename__ = "usage_statistics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Integer, nullable=False)  # in milliseconds
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="usage_statistics")

    def __repr__(self):
        return f"<UsageStatistic(id={self.id}, organization_id={self.organization_id}, endpoint='{self.endpoint}', method='{self.method}')>"
