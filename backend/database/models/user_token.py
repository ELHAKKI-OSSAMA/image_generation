from sqlalchemy import Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
class UserToken(Base):
    __tablename__ = 'user_tokens'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id'))
    token = Column(Integer, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_tokens")
