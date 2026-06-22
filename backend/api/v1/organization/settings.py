from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from database.models import Organization, User, UserProfile
from services.organization_service import OrganizationService
from schemas.organization import OrganizationSettingsUpdate, OrganizationSettingsResponse
from uuid import UUID

router = APIRouter(prefix="/organization_settings", tags=["Organization Settings"])

@router.get("/{org_id}", response_model=OrganizationSettingsResponse)
async def get_organization_settings(org_id: UUID, db: AsyncSession = Depends(get_db)):
	service = OrganizationService(db)
	result = await service.get_settings(org_id)
	if not result:
		raise HTTPException(404, "Organization not found")
	return result

@router.put("/{org_id}", response_model=OrganizationSettingsResponse)
async def update_organization_settings(org_id: UUID, data: OrganizationSettingsUpdate, db: AsyncSession = Depends(get_db)):
	service = OrganizationService(db)
	result = await service.update_settings(org_id, data.dict(exclude_unset=True))
	if not result:
		raise HTTPException(404, "Organization not found")
	return result

@router.post("/{org_id}/avatar", response_model=OrganizationSettingsResponse)
async def upload_organization_avatar(org_id: UUID, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
	org = await db.get(Organization, org_id)
	if not org:
		raise HTTPException(404, "Organization not found")
	user_profile = await db.execute(select(UserProfile).where(UserProfile.user_id == org.owner_id))
	user_profile = user_profile.scalar_one_or_none()
	# Save file logic (local or S3)
	import os
	os.makedirs("uploads/org_avatars", exist_ok=True)
	avatar_url = f"/uploads/org_avatars/{org_id}_{file.filename}"
	with open(f"uploads/org_avatars/{org_id}_{file.filename}", "wb") as out_file:
		out_file.write(await file.read())
	service = OrganizationService(db)
	result = await service.update_avatar(org_id, avatar_url)
	return result
