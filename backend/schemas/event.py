from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class EventBase(BaseModel):
    """Base event schema with common fields"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: Optional[str] = None

class EventCreate(EventBase):
    """Schema for creating a new event"""
    organization_id: UUID

class EventUpdate(BaseModel):
    """Schema for updating an existing event"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None

class EventResponse(EventBase):
    """Schema for event response"""
    id: UUID
    organization_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    participant_count: Optional[int] = 0

    class Config:
        from_attributes = True

class EventParticipantBase(BaseModel):
    """Base schema for event participants"""
    event_id: UUID
    user_id: UUID
    status: str = "registered"

class EventParticipantCreate(EventParticipantBase):
    """Schema for creating a new event participant"""
    pass

class EventParticipantUpdate(BaseModel):
    """Schema for updating an event participant"""
    status: Optional[str] = None

class EventParticipantResponse(EventParticipantBase):
    """Schema for event participant response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
