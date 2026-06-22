from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
class Guest(Base):
    __tablename__ = 'guests'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id'))
    username = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    mail = Column(String, nullable=False)
    event_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="guests")
