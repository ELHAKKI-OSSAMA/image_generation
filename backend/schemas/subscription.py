from pydantic import BaseModel, UUID4, EmailStr, constr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SubscriptionTier(str, Enum):
    TRIAL = "trial"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class BillingInfo(BaseModel):
    billing_email: EmailStr
    billing_address: str
    payment_method_id: str

class SubscriptionPlanBase(BaseModel):
    name: SubscriptionTier
    description: Optional[str] = None
    price_monthly: int  # in cents
    price_yearly: int  # in cents
    max_users: int
    max_storage_gb: int
    max_api_calls_per_month: int
    features: Dict[str, Any]

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SubscriptionHistoryBase(BaseModel):
    organization_id: UUID4
    plan_id: UUID4
    start_date: datetime
    end_date: Optional[datetime] = None
    status: SubscriptionStatus
    payment_method_id: Optional[str] = None
    amount_paid: Optional[int] = None  # in cents
    billing_cycle: BillingCycle

class SubscriptionHistoryCreate(SubscriptionHistoryBase):
    pass

class SubscriptionHistoryResponse(SubscriptionHistoryBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SubscriptionUpdate(BaseModel):
    plan_id: UUID4
    billing_cycle: BillingCycle
    billing_info: Optional[BillingInfo] = None

class SubscriptionCancellation(BaseModel):
    reason: Optional[str] = None
    feedback: Optional[str] = None

class CurrentSubscriptionResponse(BaseModel):
    organization_id: UUID4
    current_plan: SubscriptionPlanResponse
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    billing_cycle: BillingCycle
    billing_email: Optional[str] = None
    billing_address: Optional[str] = None
    payment_method_id: Optional[str] = None
    usage: Dict[str, Any]

    class Config:
        from_attributes = True
