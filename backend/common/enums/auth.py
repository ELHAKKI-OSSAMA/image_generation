from enum import Enum, auto

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFICATION = "verification"

class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
