from firebase_admin import auth
from fastapi import HTTPException, status
from typing import Dict, Any, Optional
from models.user import User, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from services.internal_log_service import InternalLogService
from models.log import LogBase, LogLevel, LogCategory
from datetime import datetime
import os
from dotenv import load_dotenv
from database.config import settings
import json
from database.models import Admin, Organization, OrganizationMember, UserRole, VerificationStatus
from firebase_init import get_firebase_app, get_firestore_client

# Load environment variables
load_dotenv()

class FirebaseService:
    def __init__(self):
        # Ensure Firebase is initialized
        get_firebase_app()
        self.db = get_firestore_client()

    async def verify_token(self, token: str) -> Dict:
        """Verify Firebase token and return user info"""
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            try:
                print("Attempting to verify token with Firebase...")
                decoded_token = auth.verify_id_token(token)
                print(f"Token verified successfully. UID: {decoded_token['uid']}")
                
                # Get user role from Firestore
                user_doc = self.db.collection('users').document(decoded_token["uid"]).get()
                
                # If user document doesn't exist, create it with default role
                if not user_doc.exists:
                    user_data = {
                        'uid': decoded_token["uid"],
                        'email': decoded_token.get("email"),
                        'role': 'user',
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    self.db.collection('users').document(decoded_token["uid"]).set(user_data)
                    role = 'user'
                else:
                    user_data = user_doc.to_dict()
                    role = user_data.get('role', 'user')
                
                return {
                    "uid": decoded_token["uid"],
                    "email": decoded_token.get("email"),
                    "role": role
                }
            except Exception as e:
                print(f"Error verifying token with Firebase: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Could not validate credentials: {str(e)}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
        except Exception as e:
            print(f"Error in verify_token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def create_user(self, email: str, password: Optional[str] = None) -> Dict:
        """Create a new user in Firebase"""
        try:
            user_data = {
                'email': email,
                'emailVerified': False,
                'disabled': False
            }
            if password:
                user_data['password'] = password
                
            user = auth.create_user(**user_data)
            
            # Create user document in Firestore
            user_doc = {
                'uid': user.uid,
                'email': email,
                'role': 'user',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            self.db.collection('users').document(user.uid).set(user_doc)
            
            return {
                'uid': user.uid,
                'email': user.email,
                'role': 'user'
            }
            
        except Exception as e:
            print(f"Error creating user in Firebase: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create user: {str(e)}"
            )

    async def sync_user(self, firebase_user: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """
        Sync Firebase user with PostgreSQL database based on their role.
        
        Args:
            firebase_user: Dictionary containing Firebase user data
            db: AsyncSession for database operations
            
        Returns:
            Dict containing the Firebase user data
            
        Raises:
            HTTPException: If user data is invalid or sync fails
        """
        try:
            if not isinstance(firebase_user, dict) or 'uid' not in firebase_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user data format"
                )

            firebase_uid = firebase_user['uid']
            user_email = firebase_user.get('email')
            
            # Get user data from Firestore
            user_doc = self.db.collection('users').document(firebase_uid).get()
            
            if not user_doc.exists:
                print(f"No Firestore document found for user {firebase_uid}")
                return firebase_user
            
            user_data = user_doc.to_dict()
            user_role = user_data.get('role', 'user')
            
            # Sync based on role
            if user_role == 'admin':
                # Check if admin exists by either firebase_uid or email
                stmt = select(Admin).where(
                    (Admin.firebase_uid == firebase_uid) | (Admin.email == user_email)
                )
                result = await db.execute(stmt)
                admin_user = result.scalar_one_or_none()
                
                if admin_user:
                    # Update existing admin's firebase_uid if needed
                    if admin_user.firebase_uid != firebase_uid:
                        admin_user.firebase_uid = firebase_uid
                        print(f"Updated admin firebase_uid for {user_email}")
                else:
                    # Create new admin
                    admin_user = Admin(
                        email=user_email,
                        firebase_uid=firebase_uid,
                        role=UserRole.ADMIN,
                        status='active',
                        password_hash='firebase_managed'  # Since Firebase handles auth
                    )
                    db.add(admin_user)
            
            elif user_role == 'organization':
                # Check if organization exists
                stmt = select(Organization).where(Organization.contact_email == user_email)
                result = await db.execute(stmt)
                org_user = result.scalar_one_or_none()
                
                if org_user:
                    # Update organization status if needed
                    org_data = user_data.get('organization', {})
                    if 'status' in org_data:
                        org_user.status = VerificationStatus(org_data['status'])
                else:
                    # Get organization details from Firestore
                    org_data = user_data.get('organization', {})
                    org_user = Organization(
                        name=org_data.get('name', 'New Organization'),
                        contact_email=user_email,
                        contact_phone=org_data.get('phone', ''),
                        status=VerificationStatus.PENDING,
                        business_type=org_data.get('type', 'Other')
                    )
                    db.add(org_user)
            
            await db.commit()
            print(f"User synced with database: {user_email}")
            
            return firebase_user
            
        except Exception as e:
            await db.rollback()
            print(f"Error syncing user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to sync user with database: {str(e)}"
            )

    async def set_custom_claims(self, uid: str, claims: Dict):
        """Set custom claims for a Firebase user"""
        try:
            auth.set_custom_user_claims(uid, claims)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to set custom claims: {str(e)}"
            )
