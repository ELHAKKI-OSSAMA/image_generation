# routers/image_service.py
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import base64
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta

from core.database import get_db
from database.models.subscription import Subscription as SubscriptionModel
import httpx
from fastapi.responses import StreamingResponse
from fastapi import Request
from database.models.image import Image
from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.orm import Session
from api.v1.auth.dependencies import get_current_user, verify_org_access
from database.models import User,UserToken
from database.models.enums import UserRole
from sqlalchemy.future import select
from database.models import Organization
from database.models.organization import OrganizationMember
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import qrcode
import io
from fastapi.responses import FileResponse
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from sqlalchemy.future import select
import base64
import io
import os
import tempfile
from typing import Optional
from fastapi import Response
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv
import os
from jose import JWTError

from core.redis_utils import get_redis,get_guest_context
import aioredis

router = APIRouter()



class ImageGenerationRequest(BaseModel):
    source_image: str  # The base64 string of the source image
    model_id: int
    event_id: UUID | None = None 
    guest_id: UUID | None = None


class ImageGenerationResponse(BaseModel):
    generated_image: str
    qr_code: str  # Base64 encoded QR code image
    download_url: str


def create_download_token(image_id: UUID) -> str:
    """Create a JWT token for secure download"""
    expires = datetime.utcnow() + timedelta(minutes=int(os.getenv("QR_ACCESS_TOKEN_EXPIRE_MINUTES")))
    payload = {
        "sub": str(image_id),  # Using 'sub' as standard claim
        "exp": expires
    }
    return jwt.encode(
        payload,
        os.getenv("QR_SECRET_KEY"),
        algorithm=os.getenv("QR_JWT_ALGORITHM")
    )



def generate_qr_code(image_id: UUID) -> str:
    """Generate a QR code image and return as base64 string"""
    token = create_download_token(image_id)
    download_url = f"{os.getenv('BASE_URL')}/api/v1/images/download/{token}"
    
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(download_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    
    # Convert to base64
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{qr_base64}"

    


@router.post("/generate")
async def generate_image(request: ImageGenerationRequest, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user),redis_client: aioredis.Redis = Depends(get_redis)):
    # Check user permissions
    if current_user.role not in [UserRole.ORGANIZATION, UserRole.MEMBER, UserRole.USER]:
        raise HTTPException(403, "Only Organization, Member, and User roles can generate images")
        
    # For regular users, check token balance
    if current_user.role == UserRole.USER:
        token_user = await db.execute(select(UserToken).where(UserToken.user_id == current_user.id))
        token_user = token_user.scalar_one_or_none()
        if not token_user:
            raise HTTPException(403, "User has no token")
        if token_user.token < 1:
            raise HTTPException(403, "Not enough tokens available")
            
    # For organizations, check active subscription
    elif current_user.role == UserRole.ORGANIZATION:
        # Get the most recent active subscription
        subscription = await db.execute(
            select(SubscriptionModel)
            .where(
                and_(
                    SubscriptionModel.user_id == current_user.id,
                    or_(
                        SubscriptionModel.date_limite.is_(None),
                        SubscriptionModel.date_limite >= datetime.utcnow()
                    )
                )
            )
            .order_by(SubscriptionModel.date_start.desc())
            .limit(1)
        )
        subscription = subscription.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(403, "No active subscription found")
            
        # Check if subscription has expired
        if subscription.date_limite and subscription.date_limite < datetime.utcnow():
            raise HTTPException(403, "Your subscription has expired")
            
        # Additional organization-specific checks can be added here
        # For example, checking usage limits, etc.
        
    # For members, we might want to check their organization's subscription
    # This is a simplified version - you might want to expand this
    elif current_user.role == UserRole.MEMBER:
        # Get organization ID from member (implementation depends on your models)
        # org_id = current_user.organization_id
        # Then check organization's subscription similar to above
        pass
    try:
        # Decode the incoming base64 image and reassemble the data URI
        image_data = base64.b64decode(request.source_image)
        img1 = "data:image/png;base64," + request.source_image

        # (Optional) Perform any dummy processing on the image
        processed_image = base64.b64encode(image_data).decode()

        # Fetch the payload from the Model Service asynchronously
        model_service_url = os.getenv("PAYLOAD_SERVER_URL")
        if not model_service_url:
            raise HTTPException(
                status_code=500,
                detail="Internal server error: PAYLOAD_SERVER_URL not configured"
            )

        model_payload_url = f"{model_service_url}/api/v1/payloads/{request.model_id}"

        
        # Get the internal API key from environment variables
        internal_api_key = os.getenv("INTERNAL_API_KEY")
        if not internal_api_key:
            raise HTTPException(
                status_code=500,
                detail="Internal server error: INTERNAL_API_KEY not configured"
            )
        
        # Include the API key in the request headers with X-API-Key format
        headers = {
            "X-API-Key": internal_api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(model_payload_url, headers=headers)
            response.raise_for_status()
            payload = response.json()

        # Update the ControlNet arguments with the new image URI.
        try:
            controlnet_args = payload["alwayson_scripts"]["ControlNet"]["args"]
            for arg in controlnet_args:
                model = arg["model"]
                if model == "ip-adapter_instant_id_sdxl [eb2d3ec0]":
                    arg["image"]["image"] = img1
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating payload: {str(e)}")


        # Forward the modified payload to the Stable Diffusion API.
        async with httpx.AsyncClient(timeout=120) as client:
            sd_response = await client.post(os.getenv("SD_API_URL"), json=payload)
            sd_response.raise_for_status()
            result = sd_response.json()

        if current_user.role != UserRole.USER:
            org_id=select(OrganizationMember.organization_id).where(OrganizationMember.user_id == current_user.id)
            await verify_org_access(org_id, current_user, db)
            # Fetch the organization ID where the user is a member
            org_result = await db.execute(
                select(OrganizationMember.organization_id)
                .where(OrganizationMember.user_id == current_user.id)
            )
            organization_id = org_result.scalar_one_or_none()
            
            if not organization_id:
                raise HTTPException(status_code=404, detail="User is not part of any organization")
        
        if current_user.role == UserRole.USER:
            request.event_id = None
            request.guest_id = None
            organization_id = None
            token_user.token -= 1
            db.add(token_user)
            await db.commit()
            await db.refresh(token_user)  # Optional
            
        elif not request.event_id or not request.guest_id:
            event_id, guest_id = await get_guest_context(redis_client, current_user.id)
            
            if not request.event_id and event_id:
                request.event_id = UUID(event_id)
            
            if not request.guest_id and guest_id:
                request.guest_id = UUID(guest_id)
            
        if "images" in result and result["images"]:
            generated_image = result["images"][0]
            image = Image(
                image_base64=generated_image,
                organization_id=organization_id,
                event_id=request.event_id if request.event_id else None,
                model_id=request.model_id,
                user_id=current_user.id,
                guest_id=request.guest_id if request.guest_id else None
            )
            db.add(image)
            await db.commit()
            await db.refresh(image)   

            # Generate secure download URL
            token = create_download_token(image.id)
            base_url = os.getenv("BASE_URL") or "http://localhost:8000"
            download_url = f"{base_url}/api/v1/images/download/{token}"
            
            # Generate QR code
            qr_code = generate_qr_code(image.id)
            
            return ImageGenerationResponse(
                generated_image=generated_image,
                qr_code=qr_code,
                download_url=download_url
            )     
        
        else:
            raise HTTPException(status_code=500, detail="No image returned from SD API")

        # Save the generated image to the database
       
    except httpx.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(http_err)}")
    


@router.get("/download/{token}")
async def download_image(token: str, db: AsyncSession = Depends(get_db)):
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            os.getenv("QR_SECRET_KEY"),
            algorithms=[os.getenv("QR_JWT_ALGORITHM")]
        )
        image_id = payload.get("sub")
        
        if not image_id:
            raise HTTPException(status_code=400, detail="Invalid token format")
            
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    # Get image from database
    result = await db.execute(select(Image).where(Image.id == UUID(image_id)))
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Decode base64 image
        if image.image_base64.startswith("data:image"):
            image_data = image.image_base64.split(",", 1)[1]
        else:
            image_data = image.image_base64
            
        image_bytes = base64.b64decode(image_data)
        
        # Create response with proper headers
        headers = {
            "Content-Disposition": "attachment; filename=image.png",
            "Content-Length": str(len(image_bytes))
        }
        
        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type="image/png",
            headers=headers
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")