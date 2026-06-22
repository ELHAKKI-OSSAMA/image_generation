from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Enum, Float
from sqlalchemy.orm import relationship
from .base import Base
from database.models.enums import UserRole
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID as PGUUID


class Plan(Base):
    __tablename__ = 'plans'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    limite_image = Column(Integer, nullable=True)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    model_list = Column(JSON, nullable=True)  # List of models as JSON
    stockage = Column(Integer, nullable=True)  # Storage in GB
    user_type = Column(Enum(UserRole), nullable=False)
    time_limit = Column(Integer, nullable=True)  # Time limit in Days
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def __repr__(self):
        return f"<Plan(id={self.id}, price={self.price}, user_id={self.user_id})>"
