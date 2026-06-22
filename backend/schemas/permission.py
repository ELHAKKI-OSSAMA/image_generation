from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    role: str
    type: str

class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    role: str
    type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
