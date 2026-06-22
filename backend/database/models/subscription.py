from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from .base import Base
from .enums import UserRole
from datetime import datetime

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type_user = Column(Enum(UserRole), nullable=False)
    plan_id = Column(PGUUID(as_uuid=True), ForeignKey('plans.id', ondelete='CASCADE'), nullable=False)
    payment_method = Column(String, nullable=False)
    date_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_limite = Column(DateTime, nullable=True)  # End date of the plan
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    plan = relationship("Plan", back_populates="subscriptions")