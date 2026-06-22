from functools import wraps
from typing import List, Union, Optional
from fastapi import HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer

from common.constants.permissions import Permission, has_permission, has_any_permission, has_all_permissions
from database.models.user import User
from core.security import decode_jwt_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

class PermissionDependency:
    def __init__(
        self,
        permissions: Union[Permission, List[Permission]],
        require_all: bool = False,
        error_message: Optional[str] = None
    ):
        """
        Initialize permission dependency.
        
        Args:
            permissions: Single permission or list of permissions required
            require_all: If True, all permissions are required. If False, any permission is sufficient
            error_message: Custom error message for permission denied
        """
        self.permissions = [permissions] if isinstance(permissions, Permission) else permissions
        self.require_all = require_all
        self.error_message = error_message or "Permission denied"

    async def __call__(self, request: Request, token: str = Depends(oauth2_scheme)) -> User:
        try:
            # Decode JWT token and get user
            user_data = decode_jwt_token(token)
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Check permissions
            if self.require_all:
                if not has_all_permissions(user_data.permissions, self.permissions):
                    raise HTTPException(status_code=403, detail=self.error_message)
            else:
                if not has_any_permission(user_data.permissions, self.permissions):
                    raise HTTPException(status_code=403, detail=self.error_message)

            return user_data

        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

def require_permissions(
    permissions: Union[Permission, List[Permission]],
    require_all: bool = False,
    error_message: Optional[str] = None
):
    """
    Decorator for requiring permissions on API endpoints.
    
    Usage:
        @router.get("/users")
        @require_permissions([Permission.VIEW_USERS])
        async def get_users():
            ...
    
    Args:
        permissions: Single permission or list of permissions required
        require_all: If True, all permissions are required. If False, any permission is sufficient
        error_message: Custom error message for permission denied
    """
    dependency = PermissionDependency(permissions, require_all, error_message)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # The dependency will handle permission checking
            return await func(*args, **kwargs)
        
        # Add the dependency to the endpoint
        wrapper.__dependencies__ = getattr(func, '__dependencies__', []) + [Depends(dependency)]
        return wrapper
    
    return decorator

# Convenience decorators for common permission patterns
def admin_required(error_message: Optional[str] = None):
    """Require admin permissions (either ADMIN or SUPER_ADMIN role permissions)"""
    return require_permissions(
        [Permission.MANAGE_USERS, Permission.MANAGE_ORGANIZATIONS],
        require_all=True,
        error_message=error_message or "Admin access required"
    )

def super_admin_required(error_message: Optional[str] = None):
    """Require super admin permissions"""
    return require_permissions(
        Permission.ALL,
        error_message=error_message or "Super admin access required"
    )

def organization_admin_required(error_message: Optional[str] = None):
    """Require organization admin permissions"""
    return require_permissions(
        [Permission.MANAGE_ORG_MEMBERS, Permission.MANAGE_ORG_SETTINGS],
        require_all=True,
        error_message=error_message or "Organization admin access required"
    )
