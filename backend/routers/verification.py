from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from core.database import get_db
from database.models import Organization, VerificationDocument, Admin, OrganizationMember, UserRole, VerificationStatus
from schemas.verification import (
    VerificationSubmission,
    VerificationResponse,
    VerificationAction,
    VerificationDocumentResponse
)
from auth.postgresql_auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["Organization Verification"])

@router.post("/organizations/submit-verification", response_model=VerificationResponse)
async def submit_verification(
    submission: VerificationSubmission,
    current_user: OrganizationMember = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is an organization admin
    if current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can submit verification"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check if already verified
    if organization.status == VerificationStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is already verified"
        )
    
    # Update organization details
    organization.business_type = submission.business_type
    organization.business_description = submission.business_description
    organization.status = VerificationStatus.IN_REVIEW
    organization.verification_submitted_at = datetime.utcnow()
    
    # Create verification documents
    verification_docs = []
    for doc in submission.documents:
        verification_doc = VerificationDocument(
            id=uuid.uuid4(),
            organization_id=organization.id,
            document_type=doc.document_type,
            file_url=doc.file_url,
            file_name=doc.file_name,
            mime_type=doc.mime_type,
            file_size=doc.file_size,
            uploaded_by=current_user.id,
            verification_status=VerificationStatus.IN_REVIEW
        )
        verification_docs.append(verification_doc)
        db.add(verification_doc)
    
    db.commit()
    db.refresh(organization)
    
    return VerificationResponse(
        organization_id=organization.id,
        status=organization.status,
        verification_submitted_at=organization.verification_submitted_at,
        verification_notes=organization.verification_notes,
        business_type=organization.business_type,
        business_description=organization.business_description,
        approved_by=organization.approved_by,
        approved_at=organization.approved_at,
        rejected_reason=organization.rejected_reason,
        rejected_at=organization.rejected_at,
        documents=[VerificationDocumentResponse.from_orm(doc) for doc in verification_docs]
    )

@router.get("/organizations/verification-status", response_model=VerificationResponse)
async def get_verification_status(
    current_user: OrganizationMember = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get organization and its documents
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    verification_docs = db.query(VerificationDocument).filter(
        VerificationDocument.organization_id == organization.id
    ).all()
    
    return VerificationResponse(
        organization_id=organization.id,
        status=organization.status,
        verification_submitted_at=organization.verification_submitted_at,
        verification_notes=organization.verification_notes,
        business_type=organization.business_type,
        business_description=organization.business_description,
        approved_by=organization.approved_by,
        approved_at=organization.approved_at,
        rejected_reason=organization.rejected_reason,
        rejected_at=organization.rejected_at,
        documents=[VerificationDocumentResponse.from_orm(doc) for doc in verification_docs]
    )

@router.post("/admin/verifications/{org_id}/approve", response_model=VerificationResponse)
async def approve_verification(
    org_id: uuid.UUID,
    action: VerificationAction,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is an admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve verifications"
        )
    
    # Get organization and its documents
    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update organization status
    organization.status = VerificationStatus.APPROVED
    organization.approved_by = current_user.id
    organization.approved_at = datetime.utcnow()
    organization.verification_notes = action.notes
    
    # Update all documents status
    verification_docs = db.query(VerificationDocument).filter(
        VerificationDocument.organization_id == organization.id
    ).all()
    
    for doc in verification_docs:
        doc.verification_status = VerificationStatus.APPROVED
        doc.verified_by = current_user.id
        doc.verified_at = datetime.utcnow()
        doc.verification_notes = action.notes
    
    db.commit()
    db.refresh(organization)
    
    return VerificationResponse(
        organization_id=organization.id,
        status=organization.status,
        verification_submitted_at=organization.verification_submitted_at,
        verification_notes=organization.verification_notes,
        business_type=organization.business_type,
        business_description=organization.business_description,
        approved_by=organization.approved_by,
        approved_at=organization.approved_at,
        rejected_reason=organization.rejected_reason,
        rejected_at=organization.rejected_at,
        documents=[VerificationDocumentResponse.from_orm(doc) for doc in verification_docs]
    )

@router.post("/admin/verifications/{org_id}/reject", response_model=VerificationResponse)
async def reject_verification(
    org_id: uuid.UUID,
    action: VerificationAction,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is an admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reject verifications"
        )
    
    # Get organization and its documents
    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update organization status
    organization.status = VerificationStatus.REJECTED
    organization.rejected_reason = action.notes
    organization.rejected_at = datetime.utcnow()
    
    # Update all documents status
    verification_docs = db.query(VerificationDocument).filter(
        VerificationDocument.organization_id == organization.id
    ).all()
    
    for doc in verification_docs:
        doc.verification_status = VerificationStatus.REJECTED
        doc.verified_by = current_user.id
        doc.verified_at = datetime.utcnow()
        doc.verification_notes = action.notes
    
    db.commit()
    db.refresh(organization)
    
    return VerificationResponse(
        organization_id=organization.id,
        status=organization.status,
        verification_submitted_at=organization.verification_submitted_at,
        verification_notes=organization.verification_notes,
        business_type=organization.business_type,
        business_description=organization.business_description,
        approved_by=organization.approved_by,
        approved_at=organization.approved_at,
        rejected_reason=organization.rejected_reason,
        rejected_at=organization.rejected_at,
        documents=[VerificationDocumentResponse.from_orm(doc) for doc in verification_docs]
    )
