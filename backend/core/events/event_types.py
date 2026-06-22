from enum import Enum

class EventType(str, Enum):
    """Event types for organization-related events."""
    
    # Organization events
    ORG_CREATED = "organization.created"
    ORG_UPDATED = "organization.updated"
    ORG_DELETED = "organization.deleted"
    
    # Member events
    MEMBER_ADDED = "organization.member.added"
    MEMBER_REMOVED = "organization.member.removed"
    MEMBER_UPDATED = "organization.member.updated"
    
    # Role events
    ROLE_UPDATED = "organization.role.updated"
    
    # Permission events
    PERMISSION_UPDATED = "organization.permission.updated"
    
    # Status events
    STATUS_UPDATED = "organization.status.updated"
