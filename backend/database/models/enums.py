from enum import Enum, auto

class UserRole(str, Enum):
    @classmethod
    def _missing_(cls, value):
        # This allows case-insensitive matching
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None

    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    ORGANIZATION = "organization"
    MEMBER = "member"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class OrganizationStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class DocumentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    OTHER = "other"

class ParticipantStatus(str, Enum):
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    ATTENDED = "attended"

class SubscriptionTier(str, Enum):
    TRIAL = "trial"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

class AuditCategory(str, Enum):
    AUTH = "authentication"
    USER = "user"
    ADMIN = "admin"
    ORGANIZATION = "organization"
    SESSION = "session"
    SECURITY = "security"

class AuditAction(str, Enum):
    # Authentication actions
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    EMAIL_VERIFICATION_REQUEST = "email_verification_request"
    EMAIL_VERIFIED = "email_verified"
    
    # User actions
    USER_REGISTERED = "user_registered"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_SUSPENDED = "user_suspended"
    USER_BANNED = "user_banned"
    USER_ACTIVATED = "user_activated"
    
    # Admin actions
    ADMIN_CREATED = "admin_created"
    ADMIN_UPDATED = "admin_updated"
    ADMIN_DELETED = "admin_deleted"
    ADMIN_PERMISSION_GRANTED = "admin_permission_granted"
    ADMIN_PERMISSION_REVOKED = "admin_permission_revoked"
    
    # Organization actions
    ORGANIZATION_CREATED = "organization_created"
    ORGANIZATION_UPDATED = "organization_updated"
    ORGANIZATION_DELETED = "organization_deleted"
    ORGANIZATION_APPROVED = "organization_approved"
    ORGANIZATION_SUSPENDED = "organization_suspended"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    MEMBER_ROLE_UPDATED = "member_role_updated"
    
    # Session actions
    SESSION_CREATED = "session_created"
    SESSION_REFRESHED = "session_refreshed"
    SESSION_EXPIRED = "session_expired"
    SESSION_INVALIDATED = "session_invalidated"
    
    # Security actions
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    IP_BLOCKED = "ip_blocked"
    IP_UNBLOCKED = "ip_unblocked"

class AdminPermission(str, Enum):
    # System permissions
    MANAGE_SYSTEM = "manage_system"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SECURITY = "manage_security"
    
    # User management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    SUSPEND_USERS = "suspend_users"
    BAN_USERS = "ban_users"
    
    # Organization management
    MANAGE_ORGANIZATIONS = "manage_organizations"
    VIEW_ORGANIZATIONS = "view_organizations"
    APPROVE_ORGANIZATIONS = "approve_organizations"
    SUSPEND_ORGANIZATIONS = "suspend_organizations"
    
    # Admin management
    MANAGE_ADMINS = "manage_admins"
    VIEW_ADMINS = "view_admins"
    GRANT_PERMISSIONS = "grant_permissions"

class OrganizationPermission(str, Enum):
    # Organization management
    MANAGE_ORGANIZATION = "manage_organization"
    VIEW_ORGANIZATION = "view_organization"
    MANAGE_MEMBERS = "manage_members"
    VIEW_MEMBERS = "view_members"
    
    # Event management
    MANAGE_EVENTS = "manage_events"
    VIEW_EVENTS = "view_events"
    PARTICIPATE_EVENTS = "participate_events"

    # User management
    MANAGE_USERS = "manage_users"
    
    # Content management
    MANAGE_CONTENT = "manage_content"
    VIEW_CONTENT = "view_content"
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    
    # Finance management
    MANAGE_FINANCES = "manage_finances"
    VIEW_FINANCES = "view_finances"
    PROCESS_PAYMENTS = "process_payments"
    ISSUE_REFUNDS = "issue_refunds"
    
    # Integration management
    MANAGE_INTEGRATIONS = "manage_integrations"
    VIEW_INTEGRATIONS = "view_integrations"
    
    # Security management
    MANAGE_SECURITY = "manage_security"
    VIEW_SECURITY_LOGS = "view_security_logs"
    
    # Analytics and reporting
    MANAGE_ANALYTICS = "manage_analytics"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_REPORTS = "export_reports"
    
    # Settings management
    MANAGE_SETTINGS = "manage_settings"
    VIEW_SETTINGS = "view_settings"

# Rate limiting settings
RATE_LIMIT_SETTINGS = {
    "login": {
        "attempts": 999999999,
        "window_seconds": 300  # 5 minutes
    },
    "password_reset": {
        "attempts": 3,
        "window": 86400  # 24 hours
    },
    "email_verification": {
        "attempts": 3,
        "window": 86400  # 24 hours
    },
    "api": {
        "attempts": 100,
        "window": 60  # 1 minute
    }
}

# Token expiration settings
TOKEN_EXPIRATION = {
    "access_token": 3600,  # 1 hour
    "refresh_token": 604800,  # 7 days
    "verification_token": 86400,  # 24 hours
    "password_reset_token": 3600  # 1 hour
}

# Password validation settings
PASSWORD_VALIDATION = {
    "min_length": 8,
    "max_length": 128,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_numbers": True,
    "require_special": True,
    "special_chars": "!@#$%^&*"
}

# Session settings
SESSION_SETTINGS = {
    "max_sessions_per_user": 5,
    "refresh_token_rotation": True,
    "absolute_timeout": 604800,  # 7 days
    "max_failed_attempts": 999999, # Temporarily disabled by setting a high number
    "remember_me_duration": 3600
}

# Organization settings
ORGANIZATION_SETTINGS = {
    "min_name_length": 3,
    "max_name_length": 100,
    "max_description_length": 500,
    "default_member_limit": 50
}




# SD Model Related Enums
class ResizeMode(int, Enum):
    JUSTRESIZE = 0
    CROPANDRESIZE = 1
    RESIZEANDFILL = 2

# SD Model Related Enums
class Gendre(str, Enum):
    MEN = "men"
    WOMEN = "women"
    BOTH = "both"

class ControlResizeMode(str, Enum):
    JUSTRESIZE = "Just Resize"
    CROPANDRESIZE = "Crop and Resize"
    RESIZEANDFILL = "Resize and Fill"

class ControlMode(str, Enum):
    BALANCED = "Balanced"
    MYPROMTISMOREIMPORTANT = "My prompt is more important"
    CONTROLNETISMOREIMPORTANT = "ControlNet is more important"

class EventType(str, Enum):
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    MEETUP = "meetup"
    EXHIBITION = "exhibition"
    SEMINAR = "seminar"
    OTHER = "other"
    

    

    

    