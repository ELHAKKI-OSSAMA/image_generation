import os
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

import requests
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


# Import your existing models and functions
from core.database import get_db
from database.models.user import User as UserModel
from database.models.plan import Plan as PlanModel
from database.models.subscription import Subscription as SubscriptionModel
from database.models.user_token import UserToken as UserTokenModel
from api.v1.auth.dependencies import get_current_user
from database.models.enums import UserRole

load_dotenv()


router = APIRouter(
    prefix="/payment",
    tags=["payment"],
    responses={404: {"description": "Not found"}}
)

# PayPal API Configuration
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API_BASE = os.getenv("PAYPAL_API_BASE")

def get_access_token():
    response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={"Accept": "application/json"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"}
    )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="PayPal token error")
    return response.json()["access_token"]

async def get_plan(db: AsyncSession, plan_id: UUID) -> PlanModel:
    result = await db.execute(select(PlanModel).where(PlanModel.id == plan_id))
    plan = result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.post("/create-order/{plan_id}")
async def create_order(
    plan_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a PayPal order for a subscription plan
    """
    # Get plan details
    plan = await get_plan(db, plan_id)
    
    # Check if user can subscribe to this plan
    if plan.user_type != current_user.role:
        raise HTTPException(
            status_code=403,
            detail=f"This plan is for {plan.user_type.value} users only"
        )
    
    # Get base URL for return URLs
    base_url = str(request.base_url).rstrip('/')
    
    try:
        token = get_access_token()
        response = requests.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD",
                        "value": str(plan.price)
                    },
                    "description": plan.description or f"{plan.user_type.value} Subscription",
                    "custom_id": str(plan.id),
                    "reference_id": str(plan.id),  # Set both custom_id and reference_id for compatibility
                    "invoice_id": f"INV-{int(datetime.utcnow().timestamp())}"  # Add invoice ID for tracking
                }],
                "application_context": {
                    "return_url": f"{base_url}/api/v1/payment/capture-order",
                    "cancel_url": f"{base_url}/api/v1/payment/cancel"
                }
            }
        )

        data = response.json()
        if response.status_code != 201:
            raise HTTPException(status_code=500, detail=data)

        # Find approval URL
        approval_url = next(
            (link["href"] for link in data.get("links", []) 
             if link.get("rel") == "approve"),
            None
        )

        if not approval_url:
            raise HTTPException(
                status_code=500, 
                detail="No approval URL found in PayPal response"
            )

        return {
            "order_id": data["id"],
            "status": data["status"],
            "approval_url": approval_url
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating PayPal order: {str(e)}"
        )

@router.get("/capture-order")
async def capture_order(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Capture payment and create subscription
    """
    try:
        # Capture payment
        access_token = get_access_token()
        response = requests.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders/{token}/capture",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )

        data = response.json()
        if response.status_code != 201:
            raise HTTPException(
                status_code=500,
                detail=f"Payment capture failed: {data}"
            )

        if data.get("status") != "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail="Payment not completed"
            )

        # Debug: Log the full PayPal response
        print("PayPal Response:", data)
        
        # Get plan ID from purchase unit
        purchase_units = data.get("purchase_units", [])
        if not purchase_units:
            raise HTTPException(
                status_code=500,
                detail=f"No purchase units in response: {data}"
            )

        # Try to get the plan ID from different possible locations in the response
        purchase_unit = purchase_units[0]
        plan_id = (
            purchase_unit.get("reference_id") or  # Try reference_id
            purchase_unit.get("custom_id") or     # Try custom_id
            (purchase_unit.get("payments", {}).get("captures", [{}])[0].get("custom_id") if purchase_unit.get("payments", {}).get("captures") else None)  # Try captures[0].custom_id
        )
        
        if not plan_id:
            # If we still can't find the plan ID, log the full purchase unit for debugging
            print("Purchase Unit:", purchase_unit)
            raise HTTPException(
                status_code=500,
                detail=f"No plan ID found in purchase unit. Available keys: {list(purchase_unit.keys())}"
            )
            
        print(f"Extracted plan_id: {plan_id}")

        try:
            # Convert plan_id to UUID
            plan_uuid = UUID(plan_id)
            print(f"Converted plan_id to UUID: {plan_uuid}")
            
            # Get plan details
            plan = await get_plan(db, plan_uuid)
            print(f"Found plan: {plan.id} - {plan.description or 'No description'}")
            print(f"Plan details - Price: {plan.price}, Type: {plan.user_type}")
        except ValueError as ve:
            print(f"Error converting plan_id to UUID: {ve}")
            print(f"plan_id type: {type(plan_id)}, value: {plan_id}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid plan ID format: {plan_id}. Error: {str(ve)}"
            )

        # Calculate subscription end date (if applicable)
        date_limite = None
        if plan.time_limit:
            date_limite = datetime.utcnow() + timedelta(days=plan.time_limit)

        # Create subscription
        subscription = SubscriptionModel(
            user_id=current_user.id,
            plan_id=plan.id,
            type_user=current_user.role,
            payment_method="paypal",
            date_start=datetime.utcnow(),
            date_limite=date_limite
        )

        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        # If this is a USER plan, update their token balance
        if current_user.role == UserRole.USER and plan.limite_image:
            user_token = await db.execute(
                select(UserTokenModel)
                .where(UserTokenModel.user_id == current_user.id)
            )
            user_token = user_token.scalars().first()
            
            if not user_token:
                user_token = UserTokenModel(
                    user_id=current_user.id,
                    token=plan.limite_image
                )
                db.add(user_token)
            else:
                user_token.token = (user_token.token or 0) + plan.limite_image
            
            await db.commit()

        # Determine the appropriate billing page based on user role
        if current_user.role == UserRole.ORGANIZATION:
            frontend_success_url = f"{os.getenv('FRONTEND_URL', '')}/organization/billing"
        else:  # For USER role
            frontend_success_url = f"{os.getenv('FRONTEND_URL', '')}/user/billing"
            
        print(f"Redirecting to: {frontend_success_url}")
        return RedirectResponse(url=frontend_success_url)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error capturing payment: {str(e)}"
        )

@router.get("/cancel")
async def cancel_payment(current_user: UserModel = Depends(get_current_user)):
    """
    Handle payment cancellation
    """
    if current_user.role == UserRole.ORGANIZATION:
            frontend_cancel_url = f"{os.getenv('FRONTEND_URL', '')}/organization/billing"
    else:  # For USER role
            frontend_cancel_url = f"{os.getenv('FRONTEND_URL', '')}/user/billing"
            
    return RedirectResponse(url=frontend_cancel_url)
