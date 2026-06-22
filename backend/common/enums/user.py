from enum import Enum, auto

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MEMBER = "member"
    USER = "user"

class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
