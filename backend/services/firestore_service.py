from firebase_admin import firestore
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from firebase_init import get_firestore_client

class FirestoreService:
    def __init__(self):
        self.db = get_firestore_client()

    def _convert_uuid(self, value: Any) -> Any:
        """Convert UUID objects to strings for Firestore"""
        if isinstance(value, UUID):
            return str(value)
        return value

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data types that Firestore doesn't support"""
        return {k: self._convert_uuid(v) for k, v in data.items() if v is not None}

    def create_organization(self, org_id: str, org_data: Dict[str, Any]) -> None:
        """Create organization document in Firestore"""
        org_ref = self.db.collection('organizations').document(str(org_id))
        sanitized_data = self._sanitize_data(org_data)
        sanitized_data['created_at'] = datetime.utcnow()
        org_ref.set(sanitized_data)

    def create_organization_member(self, member_id: str, member_data: Dict[str, Any]) -> None:
        """Create organization member document in Firestore"""
        member_ref = self.db.collection('organization_members').document(str(member_id))
        sanitized_data = self._sanitize_data(member_data)
        sanitized_data['created_at'] = datetime.utcnow()
        member_ref.set(sanitized_data)

    def update_user_role(self, user_id: str, role: str) -> None:
        """Update or create user document with role in Firestore"""
        user_ref = self.db.collection('users').document(user_id)
        
        # Check if document exists
        doc = user_ref.get()
        if doc.exists:
            # Update existing document
            user_ref.update({
                'role': role,
                'updated_at': datetime.utcnow()
            })
        else:
            # Create new document with minimal data
            user_ref.set({
                'uid': user_id,
                'role': role,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })

    def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[Dict[str, Any]]:
        """Get user document by Firebase UID"""
        users_ref = self.db.collection('users')
        query = users_ref.where('firebase_uid', '==', firebase_uid).limit(1)
        docs = query.get()
        if not docs:
            return None
        doc = docs[0]
        return doc.to_dict() if doc.exists else None
