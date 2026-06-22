from typing import Optional, Callable
from functools import wraps
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from services.permission_service import PermissionService
from core.cache.permission_cache import PermissionCache
from core.database import get_db
from core.dependencies import get_current_user
from models.user import User

def get_permission_service(
    db: Session = Depends(get_db),
    cache: PermissionCache = Depends()
) -> PermissionService:
    return PermissionService(db, cache)

def require_permission(
    permission: str,
    organization_id: Optional[UUID] = None
):
    """Decorator to check if user has required permission."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_user),
            permission_service: PermissionService = Depends(get_permission_service),
            **kwargs
        ):
            # Get organization_id from path parameters if not provided
            org_id = organization_id
            if not org_id and 'organization_id' in kwargs:
                org_id = kwargs['organization_id']

            # Check permission
            has_permission = await permission_service.has_permission(
                current_user.id,
                permission,
                org_id
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission} required"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permissions(*permissions: str):
    """Decorator to check if user has all required permissions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_user),
            permission_service: PermissionService = Depends(get_permission_service),
            **kwargs
        ):
            # Get organization_id from path parameters if available
            org_id = kwargs.get('organization_id')

            # Check all permissions
            for permission in permissions:
                has_permission = await permission_service.has_permission(
                    current_user.id,
                    permission,
                    org_id
                )
                if not has_permission:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Permission denied: {permission} required"
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(*permissions: str):
    """Decorator to check if user has any of the required permissions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_user),
            permission_service: PermissionService = Depends(get_permission_service),
            **kwargs
        ):
            # Get organization_id from path parameters if available
            org_id = kwargs.get('organization_id')

            # Check if user has any of the permissions
            for permission in permissions:
                has_permission = await permission_service.has_permission(
                    current_user.id,
                    permission,
                    org_id
                )
                if has_permission:
                    return await func(*args, **kwargs)

            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: one of {permissions} required"
            )
        return wrapper
    return decorator
