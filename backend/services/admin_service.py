from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func, delete
from sqlalchemy.orm import selectinload
from database.models import User, Admin, Organization, OrganizationMember
from database.models.enums import UserRole, OrganizationStatus, AuditCategory, AuditAction
from services.auth_service import AuthService
from services.organization_service import OrganizationService


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)
        self.org_service = OrganizationService(db)

    async def create_admin(
        self,
        user_id: UUID,
        permissions: Dict[str, Any],
        super_admin_id: UUID,
        request: Optional[Request] = None
    ) -> Admin:
        """Create a new admin"""
        # Check if super admin
        if not await self.is_super_admin(super_admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can create admins"
            )

        # Check if user exists
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if already admin
        stmt = select(Admin).where(Admin.user_id == user_id)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already an admin"
            )

        # Create admin
        admin = Admin(
            user_id=user_id,
            permissions=permissions
        )
        self.db.add(admin)

        # Update user role
        user.role = UserRole.admin

        await self.db.commit()
        await self.db.refresh(admin)

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.create,
            category=AuditCategory.admin,
            user_id=super_admin_id,
            details=f"Created admin: {user.email}",
            request=request
        )

        return admin

    async def remove_admin(
        self,
        admin_id: UUID,
        super_admin_id: UUID,
        request: Optional[Request] = None
    ) -> None:
        """Remove an admin"""
        # Check if super admin
        if not await self.is_super_admin(super_admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can remove admins"
            )

        # Get admin
        stmt = select(Admin).where(Admin.id == admin_id)
        result = await self.db.execute(stmt)
        admin = result.scalar_one_or_none()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        # Cannot remove super admin
        stmt = select(User).where(User.id == admin.user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user and user.role == UserRole.super_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove super admin"
            )

        # Remove admin
        await self.db.delete(admin)

        # Update user role
        if user:
            user.role = UserRole.user

        await self.db.commit()

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.delete,
            category=AuditCategory.admin,
            user_id=super_admin_id,
            details=f"Removed admin: {user.email if user else admin_id}",
            request=request
        )

    async def update_admin_permissions(
        self,
        admin_id: UUID,
        permissions: Dict[str, Any],
        super_admin_id: UUID,
        request: Optional[Request] = None
    ) -> Admin:
        """Update admin permissions"""
        # Check if super admin
        if not await self.is_super_admin(super_admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can update admin permissions"
            )

        # Get admin
        stmt = select(Admin).where(Admin.id == admin_id)
        result = await self.db.execute(stmt)
        admin = result.scalar_one_or_none()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        # Cannot modify super admin permissions
        stmt = select(User).where(User.id == admin.user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user and user.role == UserRole.super_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify super admin permissions"
            )

        # Update permissions
        admin.permissions = permissions
        await self.db.commit()
        await self.db.refresh(admin)

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.update,
            category=AuditCategory.admin,
            user_id=super_admin_id,
            details=f"Updated permissions for admin: {user.email if user else admin_id}",
            request=request
        )

        return admin

    async def approve_organization(
        self,
        org_id: UUID,
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> Organization:
        """Approve an organization. Only super admins can approve organizations."""
        # Check if super admin
        if not await self.is_super_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can approve organizations"
            )

        # Get organization
        org = await self.org_service.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check if already approved
        if org.status != OrganizationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization is already {org.status}"
            )

        # Get admin record
        stmt = select(Admin).where(Admin.user_id == admin_id)
        result = await self.db.execute(stmt)
        admin = result.scalar_one_or_none()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin record not found"
            )

        # Approve organization
        org.status = OrganizationStatus.active
        org.approved_by = admin.id
        org.approved_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(org)

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.update,
            category=AuditCategory.organization,
            user_id=admin_id,
            details=f"Approved organization: {org.name}",
            request=request
        )

        return org

    async def suspend_organization(
        self,
        org_id: UUID,
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> Organization:
        """Suspend an organization. Only super admins can suspend organizations."""
        # Check if super admin
        if not await self.is_super_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can suspend organizations"
            )

        # Get organization
        org = await self.org_service.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check if already suspended
        if org.status == OrganizationStatus.suspended:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is already suspended"
            )

        # Suspend organization
        org.status = OrganizationStatus.suspended
        await self.db.commit()
        await self.db.refresh(org)

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.update,
            category=AuditCategory.organization,
            user_id=admin_id,
            details=f"Suspended organization: {org.name}",
            request=request
        )

        return org

    async def decline_organization(
        self,
        org_id: UUID,
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> None:
        """Decline a pending organization. Only super admins can decline organizations."""
        # Check if super admin
        if not await self.is_super_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can decline organizations"
            )

        # Get organization
        org = await self.org_service.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check if pending
        if org.status != OrganizationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization is not pending (current status: {org.status})"
            )

        # Delete organization
        await self.db.delete(org)
        await self.db.commit()

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.delete,
            category=AuditCategory.organization,
            user_id=admin_id,
            details=f"Declined organization: {org.name}",
            request=request
        )

    async def get_pending_organizations(self) -> List[Organization]:
        """Get all pending organizations"""
        stmt = select(Organization).where(
            Organization.status == OrganizationStatus.pending)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        # Total users
        stmt = select(func.count(User.id))
        result = await self.db.execute(stmt)
        total_users = result.scalar_one()

        # Active users (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        stmt = select(func.count(User.id)).where(
            User.last_login >= thirty_days_ago)
        result = await self.db.execute(stmt)
        active_users = result.scalar_one()

        # Total organizations
        stmt = select(func.count(Organization.id))
        result = await self.db.execute(stmt)
        total_orgs = result.scalar_one()

        # Active organizations
        stmt = select(func.count(Organization.id)).where(
            Organization.status == OrganizationStatus.active
        )
        result = await self.db.execute(stmt)
        active_orgs = result.scalar_one()

        return {
            "total_users": total_users,
            "active_users_30d": active_users,
            "total_organizations": total_orgs,
            "active_organizations": active_orgs
        }

    async def is_admin(self, user_id: UUID) -> bool:
        """Check if user is an admin"""
        stmt = select(Admin).where(Admin.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def is_super_admin(self, user_id: UUID) -> bool:
        """Check if user is a super admin"""
        stmt = select(User).where(
            and_(
                User.id == user_id,
                User.role == UserRole.SUPER_ADMIN
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_all_users(self) -> List[User]:
        """Get all users in the system"""
        stmt = select(User)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_user(
        self,
        user_id: UUID,
        data: Dict[str, Any],
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> User:
        """Update user details"""
        # Check if admin
        if not await self.is_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update users"
            )

        # Get user
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update user
        for key, value in data.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.update,
            category=AuditCategory.user,
            user_id=admin_id,
            details=f"Updated user: {user.email}",
            request=request
        )

        return user

    async def delete_user(
        self,
        user_id: UUID,
        admin_id: UUID,
        request: Optional[Request] = None
    ) -> None:
        """Delete a user"""
        # Check if admin
        if not await self.is_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete users"
            )

        # Get user
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Cannot delete super admin
        if user.role == UserRole.super_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete super admin"
            )

        # Delete user
        await self.db.delete(user)
        await self.db.commit()

        # Audit log
        await self.auth_service.create_audit_log(
            action=AuditAction.delete,
            category=AuditCategory.user,
            user_id=admin_id,
            details=f"Deleted user: {user.email}",
            request=request
        )

    async def list_users(
        self,
        status: Optional[str] = None
    ) -> List[User]:
        """List all users with optional status filter"""
        # Build query
        query = (
            select(User)
            .options(
                selectinload(User.organizations),  # Load organizations where user is owner
                selectinload(User.memberships).selectinload(OrganizationMember.organization)  # Load organizations where user is member
            )
        )

        # Apply status filter if provided
        if status:
            query = query.where(User.status == status)

        # Execute query
        result = await self.db.execute(query)
        users = result.scalars().all()
        return users

    async def get_user_all_organizations(self, user_id: UUID) -> List[Organization]:
        """Get all organizations associated with a user"""
        query = select(Organization).join(
            OrganizationMember,
            Organization.id == OrganizationMember.organization_id
        ).where(OrganizationMember.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_organizations(
        self,
        status: Optional[str] = None
    ) -> List[Organization]:
        """List all organizations with optional status filter
        
        Args:
            status: Optional status filter for organizations
            
        Returns:
            List of organizations with their owners loaded
        """
        query = (
            select(Organization)
            .options(
                selectinload(Organization.owner).load_only(
                    User.id, User.email, User.first_name, 
                    User.last_name, User.role
                )
            )
        )
        if status:
            query = query.where(Organization.status == status)
        result = await self.db.execute(query)
        return result.unique().scalars().all()
    
    async def sync_permissions_with_admin(
        self,
        user_id: UUID,
        permissions: Dict[str, Any]
    ) -> bool:
        """Sync the permissions of a user with their corresponding admin record."""
        # Check if an Admin record exists for the user
        stmt = select(Admin).where(Admin.user_id == user_id)
        result = await self.db.execute(stmt)
        admin = result.scalar_one_or_none()

        if admin:
            # Update the permissions of the Admin record
            admin.permissions = permissions
            await self.db.commit()
            await self.db.refresh(admin)
            return True
        return False
