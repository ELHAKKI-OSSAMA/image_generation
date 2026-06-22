from pydantic import BaseModel, EmailStr, UUID4, Field, ConfigDict
from datetime import datetime
from typing import Optional
from database.models.enums import UserRole, VerificationStatus

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None

class BaseSchema(BaseModel):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
