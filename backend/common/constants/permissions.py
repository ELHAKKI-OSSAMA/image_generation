from enum import Enum, auto
from typing import Dict, List, Set

# Individual permissions as enum for type safety
class Permission(str, Enum):
    # System-wide permissions
    ALL = "all"  # Super admin permission
    
    # User management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    
    # Admin management
    MANAGE_ADMINS = "manage_admins"
    VIEW_ADMINS = "view_admins"
    
    # Organization management
    MANAGE_ORGANIZATIONS = "manage_organizations"
    VIEW_ORGANIZATIONS = "view_organizations"
    APPROVE_ORGANIZATIONS = "approve_organizations"
    
    # Organization-specific permissions
    MANAGE_ORG_MEMBERS = "manage_org_members"
    VIEW_ORG_MEMBERS = "view_org_members"
    MANAGE_ORG_SETTINGS = "manage_org_settings"
    
    # Event permissions
    MANAGE_EVENTS = "manage_events"
    VIEW_EVENTS = "view_events"
    PARTICIPATE_EVENTS = "participate_events"
    
    # System settings
    MANAGE_SYSTEM = "manage_system"
    VIEW_ANALYTICS = "view_analytics"
    VIEW_ORG_ANALYTICS = "view_org_analytics"

# Group permissions for easier management
PERMISSION_GROUPS: Dict[str, List[Permission]] = {
    "user_management": [
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS
    ],
    "organization_management": [
        Permission.MANAGE_ORGANIZATIONS,
        Permission.VIEW_ORGANIZATIONS,
        Permission.APPROVE_ORGANIZATIONS
    ],
    "event_management": [
        Permission.MANAGE_EVENTS,
        Permission.VIEW_EVENTS
    ],
    "system_management": [
        Permission.MANAGE_SYSTEM,
        Permission.VIEW_ANALYTICS
    ]
}

# Default permissions for each role
DEFAULT_ROLE_PERMISSIONS: Dict[str, Dict[str, bool]] = {
    "SUPER_ADMIN": {
        Permission.ALL: True,
        **{perm: True for perm in Permission}  # All permissions explicitly set
    },
    
    "ADMIN": {
        Permission.MANAGE_USERS: True,
        Permission.VIEW_USERS: True,
        Permission.MANAGE_ORGANIZATIONS: True,
        Permission.VIEW_ORGANIZATIONS: True,
        Permission.APPROVE_ORGANIZATIONS: True,
        Permission.VIEW_ANALYTICS: True,
        Permission.MANAGE_SYSTEM: False  # Cannot manage system settings
    },
    
    "ORGANIZATION": {
        Permission.MANAGE_ORG_MEMBERS: True,
        Permission.VIEW_ORG_MEMBERS: True,
        Permission.MANAGE_ORG_SETTINGS: True,
        Permission.MANAGE_EVENTS: True,
        Permission.VIEW_EVENTS: True,
        Permission.VIEW_ORG_ANALYTICS: True
    },
    
    "USER": {
        Permission.VIEW_EVENTS: True,
        Permission.PARTICIPATE_EVENTS: True
    }
}

# Helper functions
def get_role_permissions(role: str) -> Dict[str, bool]:
    """Get the default permissions for a role."""
    return DEFAULT_ROLE_PERMISSIONS.get(role.upper(), DEFAULT_ROLE_PERMISSIONS["USER"])

def has_permission(user_permissions: Dict[str, bool], required_permission: Permission) -> bool:
    """Check if the given permissions dictionary has the required permission."""
    return user_permissions.get(Permission.ALL, False) or user_permissions.get(required_permission, False)

def has_any_permission(user_permissions: Dict[str, bool], required_permissions: List[Permission]) -> bool:
    """Check if the given permissions dictionary has any of the required permissions."""
    return any(has_permission(user_permissions, perm) for perm in required_permissions)

def has_all_permissions(user_permissions: Dict[str, bool], required_permissions: List[Permission]) -> bool:
    """Check if the given permissions dictionary has all the required permissions."""
    return all(has_permission(user_permissions, perm) for perm in required_permissions)
