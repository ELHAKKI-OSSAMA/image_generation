from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid

from core.database import get_db
from database.models import (
    Organization,
    SubscriptionPlan,
    SubscriptionHistory,
    Admin,
    OrganizationMember,
    UserRole,
    SubscriptionStatus,
    UsageStatistic
)
from schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanResponse,
    SubscriptionHistoryResponse,
    SubscriptionUpdate,
    SubscriptionCancellation,
    CurrentSubscriptionResponse,
    BillingCycle
)
from auth.postgresql_auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["Subscriptions"])

# Admin endpoints
@router.post("/admin/subscription-plans", response_model=SubscriptionPlanResponse)
async def create_subscription_plan(
    plan: SubscriptionPlanCreate,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create subscription plans"
        )
    
    db_plan = SubscriptionPlan(
        id=uuid.uuid4(),
        **plan.dict()
    )
    
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    return SubscriptionPlanResponse.from_orm(db_plan)

@router.get("/admin/subscription-plans", response_model=List[SubscriptionPlanResponse])
async def list_subscription_plans(
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list subscription plans"
        )
    
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    return [SubscriptionPlanResponse.from_orm(plan) for plan in plans]

# Organization endpoints
@router.get("/organizations/subscription-plans", response_model=List[SubscriptionPlanResponse])
async def get_available_plans(
    current_user: OrganizationMember = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    return [SubscriptionPlanResponse.from_orm(plan) for plan in plans]

@router.get("/organizations/current-subscription", response_model=CurrentSubscriptionResponse)
async def get_current_subscription(
    current_user: OrganizationMember = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get current plan details
    current_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == organization.subscription_tier
    ).first()
    
    if not current_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Get current month's usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_usage = db.query(
        func.sum(UsageStatistic.api_calls).label("total_api_calls"),
        func.sum(UsageStatistic.storage_used_bytes).label("total_storage_bytes")
    ).filter(
        UsageStatistic.organization_id == organization.id,
        UsageStatistic.date >= current_month_start
    ).first()
    
    usage = {
        "api_calls": {
            "used": current_month_usage.total_api_calls or 0,
            "limit": current_plan.max_api_calls_per_month
        },
        "storage": {
            "used_gb": round((current_month_usage.total_storage_bytes or 0) / (1024 * 1024 * 1024), 2),
            "limit_gb": current_plan.max_storage_gb
        },
        "users": {
            "current": db.query(OrganizationMember).filter(
                OrganizationMember.organization_id == organization.id
            ).count(),
            "limit": current_plan.max_users
        }
    }
    
    return CurrentSubscriptionResponse(
        organization_id=organization.id,
        current_plan=SubscriptionPlanResponse.from_orm(current_plan),
        status=organization.subscription_status,
        start_date=organization.subscription_start_date,
        end_date=organization.subscription_end_date,
        billing_cycle=BillingCycle.MONTHLY,  # This should be stored in org or subscription history
        billing_email=organization.billing_email,
        billing_address=organization.billing_address,
        payment_method_id=organization.payment_method_id,
        usage=usage
    )

@router.post("/organizations/update-subscription", response_model=CurrentSubscriptionResponse)
async def update_subscription(
    update: SubscriptionUpdate,
    current_user: OrganizationMember = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can update subscription"
        )
    
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get new plan
    new_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == update.plan_id,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not new_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found or inactive"
        )
    
    # Update billing info if provided
    if update.billing_info:
        organization.billing_email = update.billing_info.billing_email
        organization.billing_address = update.billing_info.billing_address
        organization.payment_method_id = update.billing_info.payment_method_id
    
    # Calculate subscription dates
    now = datetime.utcnow()
    if update.billing_cycle == BillingCycle.YEARLY:
        end_date = now + timedelta(days=365)
        amount = new_plan.price_yearly
    else:
        end_date = now + timedelta(days=30)
        amount = new_plan.price_monthly
    
    # Update organization subscription
    organization.subscription_tier = new_plan.name
    organization.subscription_status = SubscriptionStatus.ACTIVE
    organization.subscription_start_date = now
    organization.subscription_end_date = end_date
    organization.max_users = new_plan.max_users
    organization.max_storage_gb = new_plan.max_storage_gb
    organization.max_api_calls_per_month = new_plan.max_api_calls_per_month
    
    # Create subscription history entry
    subscription_history = SubscriptionHistory(
        id=uuid.uuid4(),
        organization_id=organization.id,
        plan_id=new_plan.id,
        start_date=now,
        end_date=end_date,
        status=SubscriptionStatus.ACTIVE,
        payment_method_id=organization.payment_method_id,
        amount_paid=amount,
        billing_cycle=update.billing_cycle
    )
    
    db.add(subscription_history)
    db.commit()
    db.refresh(organization)
    
    return await get_current_subscription(current_user, db)

@router.post("/organizations/cancel-subscription", response_model=CurrentSubscriptionResponse)
async def cancel_subscription(
    cancellation: SubscriptionCancellation,
    current_user: OrganizationMember = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can cancel subscription"
        )
    
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update organization subscription status
    organization.subscription_status = SubscriptionStatus.CANCELED
    
    # Update current subscription history entry
    current_subscription = db.query(SubscriptionHistory).filter(
        SubscriptionHistory.organization_id == organization.id,
        SubscriptionHistory.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if current_subscription:
        current_subscription.status = SubscriptionStatus.CANCELED
        current_subscription.end_date = datetime.utcnow()
    
    db.commit()
    db.refresh(organization)
    
    return await get_current_subscription(current_user, db)

@router.get("/organizations/subscription-history", response_model=List[SubscriptionHistoryResponse])
async def get_subscription_history(
    current_user: OrganizationMember = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(SubscriptionHistory).filter(
        SubscriptionHistory.organization_id == current_user.organization_id
    ).order_by(SubscriptionHistory.created_at.desc()).all()
    
    return [SubscriptionHistoryResponse.from_orm(entry) for entry in history]
