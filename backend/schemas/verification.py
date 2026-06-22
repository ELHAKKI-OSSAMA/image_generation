from pydantic import BaseModel, UUID4, EmailStr, constr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VerificationStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class DocumentType(str, Enum):
    BUSINESS_LICENSE = "business_license"
    TAX_ID = "tax_id"
    IDENTITY_PROOF = "identity_proof"
    OTHER = "other"

class VerificationDocumentBase(BaseModel):
    document_type: DocumentType
    file_name: str
    mime_type: str
    file_size: Optional[int] = None

class VerificationDocumentCreate(VerificationDocumentBase):
    file_url: str

class VerificationDocumentResponse(VerificationDocumentBase):
    id: UUID4
    organization_id: UUID4
    file_url: str
    uploaded_by: UUID4
    uploaded_at: datetime
    verified_by: Optional[UUID4] = None
    verified_at: Optional[datetime] = None
    verification_status: VerificationStatus
    verification_notes: Optional[str] = None

    class Config:
        from_attributes = True

class VerificationSubmissionBase(BaseModel):
    business_type: str
    business_description: str

class VerificationSubmission(VerificationSubmissionBase):
    documents: List[VerificationDocumentCreate]

class VerificationResponse(BaseModel):
    organization_id: UUID4
    status: VerificationStatus
    verification_submitted_at: datetime
    verification_notes: Optional[str] = None
    business_type: str
    business_description: str
    approved_by: Optional[UUID4] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    rejected_at: Optional[datetime] = None
    documents: List[VerificationDocumentResponse]

    class Config:
        from_attributes = True

class VerificationAction(BaseModel):
    notes: Optional[str] = None
