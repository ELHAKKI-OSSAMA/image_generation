from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, desc
from datetime import timedelta


from core.database import get_db
from database.models.plan import Plan as PlanModel
from database.models.user_token import UserToken as UserTokenModel
from database.models.subscription import Subscription as SubscriptionModel
from database.models.user import User as UserModel
from database.models.enums import UserRole
from api.v1.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/plans_subsciprtion",
    tags=["plans_subsciprtion"],
    responses={404: {"description": "Not found"}, 403: {"description": "Forbidden - Insufficient permissions"}}
)

# Pydantic Schemas
class PlanBase(BaseModel):
    limite_image: Optional[int] = Field(None, description="Maximum number of images allowed (null for unlimited)")
    price: float = Field(..., gt=0, description="Price amount")
    description: Optional[str] = Field(None, description="Description of the plan")
    model_list: Optional[List[str]] = Field(None, description="List of model IDs accessible with this plan")
    stockage: Optional[int] = Field(None, description="Storage limit in MB (null for unlimited)")
    user_type: UserRole = Field(..., description="Type of user this plan is for")
    time_limit: Optional[int] = Field(None, description="Time limit in days (null for lifetime)")

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    limite_image: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
    model_list: Optional[List[str]] = None
    stockage: Optional[int] = None
    user_type: Optional[UserRole] = None
    time_limit: Optional[int] = None

class PlanSchema(PlanBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class SubscriptionBase(BaseModel):
    user_id: UUID = Field(..., description="ID of the user who owns this subscription")
    type_user: UserRole = Field(..., description="Type of user for this subscription")
    plan_id: UUID = Field(..., description="ID of the subscribed plan")
    payment_method: str = Field(..., description="Payment method used for this subscription")
    date_limite: Optional[datetime] = Field(None, description="Expiration date of the subscription (null for lifetime)")

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    type_user: Optional[UserRole] = None
    plan_id: Optional[UUID] = None
    payment_method: Optional[str] = None
    date_limite: Optional[datetime] = None

class SubscriptionCreateRequest(BaseModel):
    """Request model for creating a subscription"""
    user_id: Optional[UUID] = Field(
        default=None,
        description="User ID to subscribe (admin only). If not provided, uses the current user."
    )
    payment_method: str = Field(
        default="cash",
        description="Payment method used for the subscription"
    )

class SubscriptionSchema(SubscriptionBase):
    id: int
    date_start: datetime = Field(..., description="When the subscription started")
    model_config = ConfigDict(from_attributes=True)

# CRUD operations
async def get_plan(db: AsyncSession, plan_id: UUID) -> Optional[PlanModel]:
    result = await db.execute(select(PlanModel).where(PlanModel.id == plan_id))
    return result.scalars().first()

async def get_plans(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_type: Optional[UserRole] = None,
) -> List[PlanModel]:
    stmt = select(PlanModel)
    if user_type is not None:
        stmt = stmt.where(PlanModel.user_type == user_type)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_plan(db: AsyncSession, plan: PlanCreate) -> PlanModel:
    # Validate required fields based on user_type
    if plan.user_type == UserRole.ORGANIZATION:
        if plan.time_limit is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="time_limit is required for ORGANIZATION plans"
            )
        if plan.stockage is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="stockage is required for ORGANIZATION plans"
            )
    elif plan.user_type == UserRole.USER and plan.limite_image is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limite_image is required for USER plans"
        )
    
    db_plan = PlanModel(**plan.dict())
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)
    return db_plan

async def update_plan(
    db: AsyncSession,
    plan_id: UUID,
    plan_data: PlanUpdate,
) -> Optional[PlanModel]:
    db_plan = await get_plan(db, plan_id)
    if db_plan:
        for key, value in plan_data.dict(exclude_unset=True).items():
            setattr(db_plan, key, value)
        await db.commit()
        await db.refresh(db_plan)
    return db_plan

async def delete_plan(db: AsyncSession, plan_id: UUID) -> Optional[PlanModel]:
    db_plan = await get_plan(db, plan_id)
    if db_plan:
        await db.delete(db_plan)
        await db.commit()
    return db_plan

async def get_subscription(
    db: AsyncSession,
    subscription_id: int,
) -> Optional[SubscriptionModel]:
    result = await db.execute(
        select(SubscriptionModel).where(SubscriptionModel.id == subscription_id)
    )
    return result.scalars().first()

async def get_subscriptions_by_user(
    db: AsyncSession,
    user_id: UUID,
    active_only: bool = True,
) -> List[SubscriptionModel]:
    stmt = select(SubscriptionModel).where(SubscriptionModel.user_id == user_id)
    if active_only:
        stmt = stmt.where(
            or_(
                SubscriptionModel.date_limite.is_(None),
                SubscriptionModel.date_limite > datetime.utcnow(),
            )
        )
    stmt = stmt.order_by(desc(SubscriptionModel.date_start))
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_subscription(
    db: AsyncSession,
    subscription: SubscriptionCreate,
) -> SubscriptionModel:
    db_sub = SubscriptionModel(**subscription.dict(), date_start=datetime.utcnow())
    db.add(db_sub)
    await db.commit()
    await db.refresh(db_sub)
    return db_sub

async def update_subscription(
    db: AsyncSession,
    subscription_id: int,
    sub_data: SubscriptionUpdate,
) -> Optional[SubscriptionModel]:
    db_sub = await get_subscription(db, subscription_id)
    if db_sub:
        for key, value in sub_data.dict(exclude_unset=True).items():
            setattr(db_sub, key, value)
        await db.commit()
        await db.refresh(db_sub)
    return db_sub

async def delete_subscription(
    db: AsyncSession,
    subscription_id: int,
) -> Optional[SubscriptionModel]:
    db_sub = await get_subscription(db, subscription_id)
    if db_sub:
        await db.delete(db_sub)
        await db.commit()
    return db_sub

# API Endpoints
@router.post(
    "/",
    response_model=PlanSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new plan",
)
async def create_plan_endpoint(
    plan: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> PlanSchema:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can create plans",
        )
    return await create_plan(db, plan)

@router.get(
    "/",
    response_model=List[PlanSchema],
    summary="List all plans",
)
async def read_plans(
    skip: int = 0,
    limit: int = 100,
    user_type: Optional[UserRole] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> List[PlanSchema]:
    if current_user.role == UserRole.SUPER_ADMIN:
        plans = await get_plans(db, skip, limit, user_type)
    elif current_user.role in [UserRole.ORGANIZATION, UserRole.USER]:
        plans = await get_plans(db, skip, limit, current_user.role)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized",
        )
    return plans

@router.get(
    "/{plan_id}",
    response_model=PlanSchema,
    summary="Get plan by ID",
)
async def read_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> PlanSchema:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admin")
    plan = await get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan

@router.put(
    "/{plan_id}",
    response_model=PlanSchema,
    summary="Update a plan",
)
async def update_plan_endpoint(
    plan_id: UUID,
    plan_data: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> PlanSchema:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admin")
    plan = await update_plan(db, plan_id, plan_data)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan

@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a plan",
)
async def delete_plan_endpoint(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> None:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admin")
    plan = await delete_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return None

@router.get(
    "/subscriptions/me",
    response_model=List[SubscriptionSchema],
    summary="Get my subscriptions",
)
async def read_my_subscriptions(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> List[SubscriptionSchema]:
    if current_user.role not in [UserRole.ORGANIZATION, UserRole.USER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    subs = await get_subscriptions_by_user(db, current_user.id, active_only)
    return subs

@router.post(
    "/{plan_id}/subscribe",
    response_model=SubscriptionSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Subscribe to a plan",
)
async def subscribe_to_plan(
    plan_id: UUID,
    request: SubscriptionCreateRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> SubscriptionSchema:
    # Determine target user
    target_user_id = request.user_id if request.user_id is not None else current_user.id
    
    # If user_id is provided in request body, only allow SUPER_ADMIN to proceed
    if request.user_id is not None and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can subscribe other users"
        )
    
    # Get the plan
    plan = await get_plan(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Get the target user
    result = await db.execute(select(UserModel).where(UserModel.id == target_user_id))
    target_user = result.scalars().first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user role matches plan type
    if target_user.role != plan.user_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan is for {plan.user_type.value} users, but user is {target_user.role.value}"
        )
    
    # Handle token addition for USER role
    if target_user.role == UserRole.USER and plan.limite_image:
        result = await db.execute(
            select(UserTokenModel)
            .where(UserTokenModel.user_id == target_user.id)
        )
        user_token = result.scalars().first()
        
        if not user_token:
            user_token = UserTokenModel(
                user_id=target_user.id,
                token=plan.limite_image or 0
            )
            db.add(user_token)
        else:
            user_token.token = (user_token.token or 0) + (plan.limite_image or 0)
        
        await db.commit()
        await db.refresh(user_token)
    
    # Calculate date_limite for ORGANIZATION users
    date_limite = None
    if target_user.role == UserRole.ORGANIZATION and plan.time_limit:
        date_limite = datetime.utcnow() + timedelta(days=plan.time_limit)
    
    # Create subscription
    sub_data = SubscriptionCreate(
        user_id=target_user.id,
        type_user=target_user.role,  # Use target user's role, not current user's
        plan_id=plan_id,
        payment_method=request.payment_method,
        date_limite=date_limite,
    )
    
    subscription = await create_subscription(db, sub_data)
    await db.refresh(subscription)
    return subscription

@router.get(
    "/subscriptions/current",
    response_model=SubscriptionSchema,
    summary="Get current subscription",
)
async def read_current_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> SubscriptionSchema:
    if current_user.role not in [UserRole.ORGANIZATION, UserRole.MEMBER, UserRole.USER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    current_date = datetime.utcnow()
    result = await db.execute(
        select(SubscriptionModel)
        .where(
            SubscriptionModel.user_id == current_user.id,
            or_(
                SubscriptionModel.date_limite.is_(None),
                SubscriptionModel.date_limite >= current_date,
            ),
        )
        .order_by(desc(SubscriptionModel.date_start))
        .limit(1)
    )
    subscription = result.scalars().first()
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found")
    return subscription

@router.get(
    "/admin/subscriptions",
    response_model=List[SubscriptionSchema],
    summary="Get all subscriptions (Super Admin only)",
    description="Retrieve all subscriptions across all users. Requires SUPER_ADMIN role."
)
async def get_all_subscriptions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> List[SubscriptionSchema]:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required")
    
    result = await db.execute(
        select(SubscriptionModel)
        .order_by(desc(SubscriptionModel.date_start))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

class SubscriptionPeriod(BaseModel):
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    days_remaining: Optional[float]
    days_used: float
    total_days: Optional[float]
    
class OrganizationSubscriptionSummary(BaseModel):
    current_period: Optional[SubscriptionPeriod]
    all_periods: List[SubscriptionPeriod]
    total_active_days: float
    total_remaining_days: float
    has_active_subscription: bool
    active_until: Optional[datetime]

@router.get(
    "/organization/summary",
    response_model=OrganizationSubscriptionSummary,
    summary="Get organization subscription summary",
    description="Get subscription summary for the current organization user"
)
async def get_organization_summary(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> OrganizationSubscriptionSummary:
    if current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access required")
    
    # Get all active subscriptions for the organization with plan details
    now = datetime.utcnow()
    result = await db.execute(
        select(SubscriptionModel)
        .options(joinedload(SubscriptionModel.plan))  # Include plan relationship
        .where(
            SubscriptionModel.user_id == current_user.id,
            or_(
                SubscriptionModel.date_limite.is_(None),
                SubscriptionModel.date_limite >= now
            )
        )
        .order_by(desc(SubscriptionModel.date_start))
    )
    active_subscriptions = result.unique().scalars().all()
    
    periods = []
    total_active_days = 0.0
    total_remaining_days = 0.0
    has_active = False
    
    for sub in active_subscriptions:
        if sub.date_limite is None:
            # Lifetime subscription
            days_used = (now - sub.date_start).total_seconds() / 86400
            period = SubscriptionPeriod(
                start_date=sub.date_start,
                end_date=None,
                is_active=True,
                days_remaining=None,
                days_used=days_used,
                total_days=None
            )
            periods.append(period)
            total_active_days += days_used
            has_active = True
            break  # Lifetime subscription takes precedence
            
        # Calculate time differences for time-limited subscriptions
        total_seconds = (sub.date_limite - sub.date_start).total_seconds()
        total_days = total_seconds / 86400
        
        if now < sub.date_limite:
            # Active subscription
            used_seconds = (now - sub.date_start).total_seconds()
            remaining_seconds = (sub.date_limite - now).total_seconds()
            
            period = SubscriptionPeriod(
                start_date=sub.date_start,
                end_date=sub.date_limite,
                is_active=True,
                days_remaining=remaining_seconds / 86400,
                days_used=used_seconds / 86400,
                total_days=total_days
            )
            total_active_days += used_seconds / 86400
            total_remaining_days += remaining_seconds / 86400
            has_active = True
        else:
            # Expired subscription
            period = SubscriptionPeriod(
                start_date=sub.date_start,
                end_date=sub.date_limite,
                is_active=False,
                days_remaining=0,
                days_used=total_days,
                total_days=total_days
            )
            total_active_days += total_days
        
        periods.append(period)
    
    # Sort periods by start date (newest first)
    periods.sort(key=lambda p: p.start_date, reverse=True)
    
    # Calculate active_until based on remaining days to ensure consistency
    active_until = None
    if has_active and total_remaining_days > 0:
        active_until = now + timedelta(days=total_remaining_days)
    
    return OrganizationSubscriptionSummary(
        current_period=next((p for p in periods if p.is_active), None),
        all_periods=periods,
        total_active_days=total_active_days,
        total_remaining_days=total_remaining_days,
        has_active_subscription=has_active,
        active_until=active_until
    )
