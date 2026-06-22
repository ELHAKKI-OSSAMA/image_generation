from database.models.base import Base
from sqlalchemy import Table,Column, Integer,Enum, String, ForeignKey,UniqueConstraint, DateTime, Boolean, NUMERIC, func, Enum, text,JSON
from sqlalchemy.sql import func
from database.models.enums import OrganizationPermission, UserRole

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    type = Column(Enum(OrganizationPermission), nullable=True)
    created_at = Column(DateTime, server_default=func.now())