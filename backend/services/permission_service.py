from typing import List, Optional, Set
from uuid import UUID
from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.permissions import Permission, RolePermission, UserPermission
from models.user import User
from common.enums.user import UserRole
from core.cache.permission_cache import PermissionCache

class PermissionService:
    def __init__(self, db: Session, cache: PermissionCache):
        self.db = db
        self.cache = cache

    async def get_user_permissions(
        self, 
        user_id: UUID, 
        organization_id: Optional[UUID] = None
    ) -> Set[str]:
        """Get all permissions for a user, including role-based and direct permissions"""
        # Try cache first
        cache_key = f"perm:{user_id}:{organization_id or 'global'}"
        cached_permissions = await self.cache.get(cache_key)
        if cached_permissions:
            return set(cached_permissions)

        # Get user with role
        user = await self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get role-based permissions
        role_perms = await self.db.query(Permission.name).join(
            RolePermission,
            and_(
                RolePermission.permission_id == Permission.id,
                RolePermission.role == user.role
            )
        ).all()
        permissions = {perm.name for perm in role_perms}

        # Get direct user permissions
        user_perms_query = self.db.query(Permission.name).join(
            UserPermission,
            and_(
                UserPermission.permission_id == Permission.id,
                UserPermission.user_id == user_id,
                UserPermission.is_active == True,
                or_(
                    UserPermission.expires_at.is_(None),
                    UserPermission.expires_at > datetime.utcnow()
                )
            )
        )

        # Filter by organization if specified
        if organization_id:
            user_perms_query = user_perms_query.filter(
                or_(
                    UserPermission.organization_id.is_(None),
                    UserPermission.organization_id == organization_id
                )
            )

        user_perms = user_perms_query.all()
        permissions.update(perm.name for perm in user_perms)

        # Cache the results
        await self.cache.set(cache_key, list(permissions))

        return permissions

    async def has_permission(
        self, 
        user_id: UUID, 
        permission: str, 
        organization_id: Optional[UUID] = None
    ) -> bool:
        """Check if a user has a specific permission"""
        user_permissions = await self.get_user_permissions(user_id, organization_id)
        return permission in user_permissions

    async def grant_permission(
        self,
        user_id: UUID,
        permission_name: str,
        granted_by: UUID,
        organization_id: Optional[UUID] = None,
        expires_at: Optional[datetime] = None
    ) -> None:
        """Grant a permission to a user"""
        # Get permission
        permission = await self.db.query(Permission).filter(
            Permission.name == permission_name
        ).first()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        # Check for existing permission
        existing = await self.db.query(UserPermission).filter(
            and_(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission.id,
                UserPermission.organization_id == organization_id
            )
        ).first()

        if existing:
            # Update existing permission
            existing.is_active = True
            existing.expires_at = expires_at
            existing.granted_by = granted_by
        else:
            # Create new permission
            user_permission = UserPermission(
                user_id=user_id,
                permission_id=permission.id,
                organization_id=organization_id,
                granted_by=granted_by,
                expires_at=expires_at
            )
            self.db.add(user_permission)

        await self.db.commit()
        
        # Invalidate cache
        cache_key = f"perm:{user_id}:{organization_id or 'global'}"
        await self.cache.delete(cache_key)

    async def revoke_permission(
        self,
        user_id: UUID,
        permission_name: str,
        organization_id: Optional[UUID] = None
    ) -> None:
        """Revoke a permission from a user"""
        # Get permission
        permission = await self.db.query(Permission).filter(
            Permission.name == permission_name
        ).first()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        # Update permission
        result = await self.db.query(UserPermission).filter(
            and_(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission.id,
                UserPermission.organization_id == organization_id
            )
        ).update({"is_active": False})

        if result:
            await self.db.commit()
            
            # Invalidate cache
            cache_key = f"perm:{user_id}:{organization_id or 'global'}"
            await self.cache.delete(cache_key)

    async def create_permission(
        self,
        name: str,
        description: str
    ) -> Permission:
        """Create a new permission"""
        permission = Permission(name=name, description=description)
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def assign_role_permission(
        self,
        role: str,
        permission_name: str
    ) -> None:
        """Assign a permission to a role"""
        # Get permission
        permission = await self.db.query(Permission).filter(
            Permission.name == permission_name
        ).first()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        # Create role permission if it doesn't exist
        existing = await self.db.query(RolePermission).filter(
            and_(
                RolePermission.role == role,
                RolePermission.permission_id == permission.id
            )
        ).first()

        if not existing:
            role_permission = RolePermission(
                role=role,
                permission_id=permission.id
            )
            self.db.add(role_permission)
            await self.db.commit()

            # Invalidate all user caches for this role
            users = await self.db.query(User).filter(User.role == role).all()
            for user in users:
                cache_key = f"perm:{user.id}:global"
                await self.cache.delete(cache_key)
