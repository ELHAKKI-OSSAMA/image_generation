from fastapi import APIRouter
from sqlalchemy import null, select
from core.database import async_session
from pydantic import BaseModel
from core.database import get_db  # Ensure this returns an AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr
from typing import List
from uuid import uuid4
from database.models import Event
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from database.models.enums import EventType
from sqlalchemy import Enum
from database.models import User, OrganizationMember, Guest
from sqlalchemy import func
from fastapi import HTTPException
from database.models.enums import UserRole
from api.v1.auth.dependencies import get_current_user, verify_org_access, verify_event_access
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import insert
from core.redis_utils import set_event_context,get_redis
import aioredis


router = APIRouter(
    prefix="/event",
    tags=["event"]
)

class EventBase(BaseModel):
    name: str | None = None
    description: str | None = None
    event_end_timed: datetime | None = None
    event_time: datetime | None = None
    active: bool | None = None
    public: bool | None = None
    type: EventType | None = None
    location: str | None = None
    attendees: int | None = None
    photos_number:int | None = None


class EventResponseWithoutUserId(EventBase):
    id: UUID
    user_name: str | None = None
    event_guests_number: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True

class EventResponse(EventBase):
    id: UUID
    organization_id: UUID
    user_id: UUID | None = None
    user_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True

class EventCreate(EventBase):
    pass


class EventContextRequest(BaseModel):
    event_id: UUID

@router.post("/set_event_context")
async def set_event_context_api(
    data: EventContextRequest,
    current_user: User = Depends(get_current_user),
    redis_client: aioredis.Redis = Depends(get_redis)
) -> dict:
    """Set event context for the current user"""
    if current_user.role not in (UserRole.ORGANIZATION, UserRole.MEMBER):
        raise HTTPException(
            status_code=403, 
            detail="Only organization and member can set event context"
        )

    await set_event_context(redis_client, current_user.id, data.event_id, ttl_seconds=3600)
    return {"message": "Event context set successfully"}

@router.get("/organization/{id}", response_model=list[EventResponseWithoutUserId])
async def get_events_by_organization(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ORGANIZATION, UserRole.MEMBER):
        raise HTTPException(
            status_code=403, 
            detail="Only super admin, organization, and member can get events"
        )
        
    if current_user.role != UserRole.SUPER_ADMIN:
        await verify_org_access(id, current_user, db)

    # First get all events for the organization
    events_result = await db.execute(
        select(Event)
        .where(Event.organization_id == id)
        .options(joinedload(Event.user))
    )
    events = events_result.scalars().all()
    
    # Get guest counts for all events in one query
    guest_counts = await db.execute(
        select(
            Guest.event_id,
            func.count(Guest.id).label('guest_count')
        )
        .where(Guest.event_id.in_([event.id for event in events]))
        .group_by(Guest.event_id)
    )
    guest_count_map = {event_id: count for event_id, count in guest_counts.all()}
    
    # Build response
    response = []
    for event in events:
        event_dict = {
            **event.__dict__,
            "user_name": f"{event.user.first_name} {event.user.last_name}" if event.user else None,
            "event_guests_number": guest_count_map.get(event.id, 0)
        }
        # Remove SQLAlchemy instance state
        event_dict.pop('_sa_instance_state', None)
        response.append(EventResponseWithoutUserId(**event_dict))
    
    return response





@router.post("/", response_model=EventResponse)
async def create_event(
    event: EventCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.ORGANIZATION, UserRole.MEMBER):
        raise HTTPException(
            status_code=403, 
            detail="Only organization and member can create events"
        )
    
    # Get organization ID for the current user
    result = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    org_member = result.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(
            status_code=400,
            detail="User is not a member of any organization"
        )
    
    org_id = org_member
    await verify_org_access(org_id, current_user, db)
    
    new_event = Event(
        id=uuid4(),
        name=event.name,
        description=event.description,
        organization_id=org_id,
        user_id=current_user.id,
        event_end_timed=event.event_end_timed,
        event_time=event.event_time,
        active=event.active,
        public=event.public,
        type=event.type,
        location=event.location,
        attendees=event.attendees
    )

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    
    return new_event


@router.get("/organization/{organization_id}/count", response_model=dict)
async def get_event_count(
    organization_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ORGANIZATION, UserRole.MEMBER):
        raise HTTPException(
            status_code=403, 
            detail="Only super admin, organization, and member can get event count"
        )
    
    if current_user.role != UserRole.SUPER_ADMIN:
        await verify_org_access(organization_id, current_user, db)
        
    result = await db.execute(
        select(func.count(Event.id))
        .where(Event.organization_id == organization_id)
        .where(Event.active == True)
    )
    event_count = result.scalar_one()
    
    return {"organization_id": organization_id, "event_count": event_count}


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update event details"""
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER :
        raise HTTPException(403, "Only organization and member can update event details")
    event_data = await verify_event_access(event_id, current_user, db)
    org = event_data["org"]
    
    # Only owner, admin, or manager can update events
    if (current_user.id != org.owner_id and 
        current_user.role != UserRole.ORGANIZATION and 
        current_user.role != UserRole.MANAGER):
        raise HTTPException(403, "Insufficient permissions to update event")
    
    updated_event = await db.execute(
        update(Event)
        .where(Event.id == event_id)
        .values(
            name=data.name if data.name else Event.name,
            description=data.description if data.description else Event.description,
            event_end_timed=data.event_end_timed if data.event_end_timed else Event.event_end_timed,
            event_time=data.event_time if data.event_time else Event.event_time,
            active=data.active if data.active else Event.active,
            public=data.public if data.public else Event.public,
            type=data.type if data.type else Event.type,
            location=data.location if data.location else Event.location,
            attendees=data.attendees if data.attendees else Event.attendees
        )
    )
    await db.commit()
    result = await db.execute(select(Event).where(Event.id == event_id))
    updated_event = result.scalar_one_or_none()

    if not updated_event:
        raise HTTPException(404, detail="Event not found after update")

    return updated_event


@router.get("/", response_model=list[EventResponse])
async def get_events(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=403, 
            detail="Only super admin can get events"
        )
        
    result = await db.execute(
        select(Event)
        .options(joinedload(Event.user))
    )
    events = result.scalars().all()
    
    # Convert to response model
    return [
        {
            **event.__dict__,
            "user_name": f"{event.user.first_name} {event.user.last_name}" if event.user else None
        }
        for event in events
    ]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get event details"""
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER :
        raise HTTPException(403, "Only organization and member can get event details")
    event_data = await verify_event_access(event_id, current_user, db)
    return event_data["event"]


   

@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an event"""
    if current_user.role != UserRole.ORGANIZATION :
        raise HTTPException(403, "Only organization can delete event")
    event_data = await verify_event_access(event_id, current_user, db)
    org = event_data["org"]
    
    # Only owner, admin, or manager can delete events
    if (current_user.id != org.owner_id and 
        current_user.role != UserRole.ORGANIZATION and 
        current_user.role != UserRole.MANAGER):
        raise HTTPException(403, "Insufficient permissions to delete event")
    await db.execute(delete(Event).where(Event.id == event_id))
    await db.commit()
    return {"message": "Event deleted successfully"}


