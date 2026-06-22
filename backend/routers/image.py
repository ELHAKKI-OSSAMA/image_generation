from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
from sqlalchemy import select
from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Image
from database.models import Organization
from database.models import Event
from database.models import Model
from database.models import OrganizationMember
from database.models import Organization
from api.v1.auth.dependencies import get_current_user, verify_org_access, get_current_admin
from fastapi import APIRouter, Depends, HTTPException, status
from database.models import User
from database.models.enums import UserRole
from api.v1.organization.routes import verify_org_access
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/image",
    tags=["image"]
)

class ImageBase(BaseModel):
    source_image: Optional[str]
    model_id: int
    organization_id: UUID
    event_id: UUID | None = None

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
        OrmMode = True  # Enables ORM mode for Pydantic models

class ImageResponse(ImageBase):
    id: UUID | None = None

    
    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
        OrmMode = True  # Enables ORM mode for Pydantic models

# Define Pydantic schema
class ImageCreate(ImageBase):
    pass



@router.get("/user/me")
async def get_all_images_of_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # If org_id is not provided, try to get it from the current user's organization
    if current_user.role != UserRole.USER:
        raise HTTPException(status_code=403, detail="Only user can get images")
    
    
    
    # Now query for images in the user's organization
    result = await db.execute(select(Image).where(Image.user_id == current_user.id))
    images = result.scalars().all()
    
    return [images]


@router.get("/user/me/count")
async def get_count_of_images_of_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # If org_id is not provided, try to get it from the current user's organization
    if current_user.role != UserRole.USER:
        raise HTTPException(status_code=403, detail="Only user can get images")
    

    

    
    
    # Now query for images in the user's organization
    result = await db.execute(select(Image).where(Image.user_id == current_user.id))
    images = result.scalars().all()
    
    return len(images)


@router.get("/organization/me")
async def get_all_images_of_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # If org_id is not provided, try to get it from the current user's organization
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only Organization and Member can get images")
    
    # Get the user's organization ID from organization_members table
    org_member = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.status == 'active')  # Only active members
    )
    org_member = org_member.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not an active member of any organization")
    
    org_id = str(org_member)
    
    # Now query for images in the user's organization
    result = await db.execute(select(Image).where(Image.organization_id == org_id))
    images = result.scalars().all()
    
    return [images]

@router.get("/organization/me/count")
async def get_count_of_images_of_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # If org_id is not provided, try to get it from the current user's organization
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only Organization and Member can get images")
    
    # Get the user's organization ID from organization_members table
    org_member = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.status == 'active')  # Only active members
    )
    org_member = org_member.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not an active member of any organization")
    
    org_id = str(org_member)
    
    # Now query for images in the user's organization
    result = await db.execute(select(Image).where(Image.organization_id == org_id))
    images = result.scalars().all()
    
    return len(images)

@router.delete("/user/{image_id}")
async def delete_image_by_organization_id(image_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.USER:
        raise HTTPException(status_code=403, detail="Only user can delete images")
    result = await db.execute(select(Image).where(Image.id == image_id))
    if current_user.id != result.scalar_one_or_none().user_id:
        raise HTTPException(status_code=403, detail="Only creator of the image can delete it")
    image = result.scalar_one_or_none()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    await db.delete(image)
    await db.commit()
    return {"message": "Image deleted successfully"}

@router.get("/organization/me/count/last_month")
async def get_count_of_images_of_organization_last_month(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # If org_id is not provided, try to get it from the current user's organization
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only Organization and Member can get images")
    
    # Get the user's organization ID from organization_members table
    org_member = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.status == 'active')  # Only active members
    )
    org_member = org_member.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not an active member of any organization")
    
    org_id = str(org_member)
    
    # Now query for images in the user's organization
    result = await db.execute(select(Image).where(Image.organization_id == org_id).where(Image.created_at >= datetime.now() - timedelta(days=30)))
    images = result.scalars().all()
    
    return len(images)


@router.get("/organization/me/event/{event_id}")
async def get_images_of_my_organization_by_event_id(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only Organization and Member can get images")
    
    org_member = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.status == 'active')  # Only active members
    )
    org_member = org_member.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not an active member of any organization")
    
    org_id = str(org_member)
    # Verify the user has access to this organization
    await verify_org_access(org_id, current_user, db)

    # Now query for images
    result = await db.execute(
        select(Image)
        .where(Image.organization_id == org_id)
        .where(Image.event_id == event_id)
    )
    images = result.scalars().all()
    
    return [images]




@router.get("/organization/me/model/{model_id}")
async def get_images_by_organization_id(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)

):
    org_member = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.status == 'active')  # Only active members
    )
    org_member = org_member.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not an active member of any organization")
    
    org_id = str(org_member)
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only Organization and Member can get images")
    
    # Verify the user has access to this organization
    await verify_org_access(org_id, current_user, db)
    
    # Now query for images
    result = await db.execute(
        select(Image)
        .where(Image.organization_id == org_id)
        .where(Image.model_id == model_id)
    )
    images = result.scalars().all()
    return [images]
    
@router.get("/organization/me/model/{model_id}/event/{event_id}")
async def get_images_by_organization_id(
    model_id: int,
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_member = await db.execute(
        select(OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.status == 'active')  # Only active members
    )
    org_member = org_member.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not an active member of any organization")
    
    org_id = str(org_member)
    if current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER:
        raise HTTPException(status_code=403, detail="Only Organization and Member can get images")
    
    # Verify the user has access to this organization
    await verify_org_access(org_id, current_user, db)
    
    # Now query for images
    result = await db.execute(
        select(Image)
        .where(Image.organization_id == org_id)
        .where(Image.model_id == model_id)
        .where(Image.event_id == event_id)
    )
    images = result.scalars().all()
    return [images]    




@router.get("/organization/id/{organization_id}")
async def get_image_by_organization_id(organization_id: UUID, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can get images")
    result = await db.execute(select(Image).where(Image.organization_id == organization_id))
    images = result.scalars().all()
    return [ImageResponse.model_validate(image) for image in images]

@router.get("/event/id/{event_id}")
async def get_image_by_event_id(event_id: UUID, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can get images")
    result = await db.execute(select(Image).where(Image.event_id == event_id))
    images = result.scalars().all()
    return [ImageResponse.model_validate(image) for image in images]

@router.get("/model/id/{model_id}")
async def get_image_by_model_id(model_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)): 
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can get images")
    result = await db.execute(select(Image).where(Image.model_id == model_id))
    images = result.scalars().all()
    return [ImageResponse.model_validate(image) for image in images]

@router.get("/all")
async def get_all_images(db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can get images")
    result = await db.execute(select(Image))
    images = result.scalars().all()
    return [ImageResponse.model_validate(image) for image in images]

@router.get("/user/me")
async def get_image_by_user_id(current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.USER :
        raise HTTPException(status_code=403, detail="Only user can get images")
    result = await db.execute(select(Image).where(Image.user_id == current_user.id))
    images = result.scalars().all()
    return [ImageResponse.model_validate(image) for image in images]

@router.get("/user/id/{user_id}")
async def get_image_by_user_id(user_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can get images")
    result = await db.execute(select(Image).where(Image.user_id == user_id))
    images = result.scalars().all()
    return [ImageResponse.model_validate(image) for image in images]

@router.delete("/id/{id}")
async def delete_image_by_id(id: UUID, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can delete images")
    result = await db.execute(select(Image).where(Image.id == id))
    image = result.scalar_one_or_none()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    await db.delete(image)
    await db.commit()
    return {"message": "Image deleted successfully"}


@router.delete("/organization/{image_id}")
async def delete_image_by_organization_id(image_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(status_code=403, detail="Only organization admin can delete images")
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if current_user.id != image.organization_id:
        raise HTTPException(status_code=403, detail="Only organization admin can delete images")
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    await db.delete(image)
    await db.commit()
    return {"message": "Image deleted successfully"}

@router.get("/id/{id}")
async def get_images_by_id(id: UUID, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(status_code=403, detail="Only super admin can get images")
    result = await db.execute(select(Image).where(Image.id == id))
    images = result.scalars().all()
    return [ImageResponse.model_validate(image) for image in images]


@router.get("/root")
async def root():
    return {"message": "Router Image Running"}
