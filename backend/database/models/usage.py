from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from database.base import Base

class UsageStatistic(Base):
    __tablename__ = "usage_statistics"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    organization_id = Column(PostgresUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    api_calls = Column(Integer, default=0)
    storage_bytes = Column(Integer, default=0)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
