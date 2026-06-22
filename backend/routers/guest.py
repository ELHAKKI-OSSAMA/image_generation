from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from core.database import get_db
from database.models import Guest, Event, User, OrganizationMember
from database.models.enums import UserRole
from api.v1.auth.dependencies import get_current_user, verify_org_access
from pydantic import BaseModel
from uuid import uuid4
from core.redis_utils import set_guest_context,get_redis,get_event_context
import aioredis

router = APIRouter(prefix="/guests", tags=["guests"])

# Pydantic models
class GuestBase(BaseModel):
    username: str
    last_name: str
    first_name: str
    phone_number: str
    mail: str
    event_id: UUID | None = None
    
    

class GuestCreate(GuestBase):
    pass

class GuestUpdate(BaseModel):
    username: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    phone_number: Optional[str] = None
    mail: Optional[str] = None
    event_id: UUID | None = None

class GuestResponse(GuestBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True



# CRUD Endpoints
@router.post("/", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
async def create_guest(
    guest: GuestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis_client: aioredis.Redis = Depends(get_redis)
):
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.USER :
        raise HTTPException(status_code=403, detail="Only organization and user can create guests")
    

    
    org_id=select(OrganizationMember.organization_id).where(OrganizationMember.user_id == current_user.id)
    await verify_org_access(org_id, current_user, db)
    if not guest.event_id:
        guest.event_id = await get_event_context(redis_client, current_user.id)
        if not guest.event_id:
           guest.event_id = None


    if guest.event_id:
        event_result = await db.execute(
            select(Event)
            .where(Event.id == guest.event_id)
            .where(Event.organization_id == org_id)
        )
        if not event_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
    # Check if username already exists for this event
    result = await db.execute(
        select(Guest)
        .where(Guest.username == guest.username)
        .where(Guest.event_id == guest.event_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

   

    # Create new guest
    db_guest = Guest(
        id=uuid4(),
        user_id=current_user.id,
        **guest.model_dump()
    )
    
    db.add(db_guest)
    await db.commit()
    await db.refresh(db_guest)
    
    await set_guest_context(redis_client, current_user.id, guest.event_id, db_guest.id, ttl_seconds=3600)
    
    return db_guest


class GuestListRequest(BaseModel):
    event_id: UUID | None = None
    skip: int = 0
    limit: int = 100

from typing import Dict, List, Union, Any

@router.post("/list")
async def list_guests(
    request: GuestListRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Union[Dict[UUID, List[Dict[str, Any]]], List[Dict[str, Any]]]:
    event_id = request.event_id if request else None
    skip = request.skip if request else 0
    limit = request.limit if request else 100
    
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER :
        raise HTTPException(status_code=403, detail="Only organization and member can list guests")
    
    # Get organization ID for the current user
    org_result = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    org_id = org_result.scalar_one_or_none()
    
    if not org_id:
        return []
        
    await verify_org_access(org_id, current_user, db)
    
    # Build base query
    query = select(Guest).where(
        Guest.user_id.in_(
            select(OrganizationMember.user_id)
            .where(OrganizationMember.organization_id == org_id)
        )
    )
    
    # Add event filter if specified
    if event_id:
        query = query.where(Guest.event_id == event_id)
    else:
        # Filter by organization members
        org_members_query = select(OrganizationMember.user_id).where(OrganizationMember.organization_id == org_id)
        query = query.where(Guest.user_id.in_(org_members_query))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    guests = result.scalars().all()
    
    # Convert guests to list of dicts
    guests_list = [
        {
            "id": guest.id,
            "username": guest.username,
            "event_id": guest.event_id,
            "user_id": guest.user_id,
            "created_at": guest.created_at.isoformat() if guest.created_at else None,
            "updated_at": guest.updated_at.isoformat() if guest.updated_at else None
        }
        for guest in guests
    ]
    
    # If no event_id is provided, group by event_id
    if not event_id:
        grouped_guests = {}
        for guest in guests_list:
            event_id = guest["event_id"]
            if event_id not in grouped_guests:
                grouped_guests[event_id] = []
            grouped_guests[event_id].append(guest)
        return grouped_guests
        
    # If event_id is provided, return as a list
    return guests_list


from sqlalchemy import func, select as sa_select, exists
from typing import Dict, Any

class CountGuestsRequest(BaseModel):
    event_id: UUID | None = None
    
    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Dict
from uuid import UUID

class CountGuestsResponse(BaseModel):
    data: Dict[UUID, int]
    total: int


@router.post("/count", response_model=CountGuestsResponse)
async def count_guests(
    request: CountGuestsRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.ORGANIZATION, UserRole.MEMBER):
        raise HTTPException(status_code=403, detail="Only organization and member can count guests")
    
    event_id = request.event_id if request else None

    org_result = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    org_id = org_result.scalar_one_or_none()

    if not org_id:
        return {"data": {}, "total": 0}
        
    await verify_org_access(org_id, current_user, db)

    if event_id:
        # Count for specific event
        query = select(func.count()).select_from(Guest).where(
            Guest.event_id == event_id,
            Guest.user_id.in_(
                select(OrganizationMember.user_id)
                .where(OrganizationMember.organization_id == org_id)
            )
        )
        result = await db.execute(query)
        count = result.scalar_one()
        return {
            "data": {event_id: count},
            "total": count
        }
    else:
        # Count grouped by event_id
        query = select(
            Guest.event_id,
            func.count(Guest.id).label('count')
        ).where(
            Guest.user_id.in_(
                select(OrganizationMember.user_id)
                .where(OrganizationMember.organization_id == org_id)
            )
        ).group_by(Guest.event_id)

        result = await db.execute(query)
        rows = result.all()
        return {
            "data": {row.event_id: row.count for row in rows},
            "total": sum(row.count for row in rows)
        }

class ConnectionRequest(BaseModel):
    event_id: UUID | None = None
    username: str
    
    class Config:
        from_attributes = True

class ConnectionResponse(BaseModel):
    exists: bool
    guest_id: Optional[str]
    
    class Config:
        from_attributes = True



@router.post("/connect", response_model=ConnectionResponse)
async def connect_guest(
    request: ConnectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis_client: aioredis.Redis = Depends(get_redis)
):
    if current_user.role not in (UserRole.ORGANIZATION, UserRole.MEMBER):
        raise HTTPException(
            status_code=403,
            detail="Only organization and member can check guest connection"
        )

    # Get organization ID
    org_result = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    org_id = org_result.scalar_one_or_none()

    if not org_id:
        return {"exists": False, "guest_id": None}

    await verify_org_access(org_id, current_user, db)
    
    if not request.event_id:
        event_id = await get_event_context(redis_client, current_user.id)
        if event_id:
            request.event_id = event_id
        else:
            request.event_id = None

    if request.event_id:
        event_result = await db.execute(
            select(Event)
            .where(Event.id == request.event_id)
            .where(Event.organization_id == org_id)
        )
        if not event_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

    # Find guest
    guest_result = await db.execute(
        select(Guest.id)
        .where(
            Guest.username == request.username,
            Guest.event_id == request.event_id,
            Guest.user_id.in_(
                select(OrganizationMember.user_id)
                .where(OrganizationMember.organization_id == org_id)
            )
        )
    )
    guest_id = guest_result.scalar_one_or_none()
    if guest_id:
        await set_guest_context(redis_client, current_user.id, request.event_id, guest_id, ttl_seconds=3600)

    return {
        "exists": True if guest_id else False,
        "guest_id": str(guest_id) if guest_id else None
    }
