import asyncio
from typing import List, Dict

from sqlalchemy.orm import Session

from models.permissions import Permission, RolePermission
from database import SessionLocal
from common.enums.user import UserRole

# Define default permissions
DEFAULT_PERMISSIONS: List[Dict[str, str]] = [
    # User Management
    {
        "name": "user:create",
        "description": "Create new users"
    },
    {
        "name": "user:read",
        "description": "View user details"
    },
    {
        "name": "user:update",
        "description": "Update user details"
    },
    {
        "name": "user:delete",
        "description": "Delete users"
    },
    
    # Organization Management
    {
        "name": "organization:create",
        "description": "Create new organizations"
    },
    {
        "name": "organization:read",
        "description": "View organization details"
    },
    {
        "name": "organization:update",
        "description": "Update organization details"
    },
    {
        "name": "organization:delete",
        "description": "Delete organizations"
    },
    
    # Event Management
    {
        "name": "event:create",
        "description": "Create new events"
    },
    {
        "name": "event:read",
        "description": "View event details"
    },
    {
        "name": "event:update",
        "description": "Update event details"
    },
    {
        "name": "event:delete",
        "description": "Delete events"
    },
    
    # Permission Management
    {
        "name": "permission:grant",
        "description": "Grant permissions to users"
    },
    {
        "name": "permission:revoke",
        "description": "Revoke permissions from users"
    },
    {
        "name": "permission:read",
        "description": "View permissions"
    }
]

# Define role permissions
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN.value: [
        "user:create", "user:read", "user:update", "user:delete",
        "organization:create", "organization:read", "organization:update", "organization:delete",
        "event:create", "event:read", "event:update", "event:delete",
        "permission:grant", "permission:revoke", "permission:read"
    ],
    UserRole.ADMIN.value: [
        "user:read", "user:update",
        "organization:read", "organization:update",
        "event:create", "event:read", "event:update", "event:delete",
        "permission:read"
    ],
    UserRole.MEMBER.value: [
        "user:read",
        "organization:read",
        "event:read"
    ]
}

async def init_permissions(db: Session):
    """Initialize default permissions and role assignments."""
    print("Initializing permissions...")
    
    # Create permissions
    for perm_data in DEFAULT_PERMISSIONS:
        perm = Permission(**perm_data)
        db.add(perm)
    
    await db.commit()
    
    # Get all permissions
    permissions = {
        p.name: p.id 
        for p in await db.query(Permission).all()
    }
    
    # Assign permissions to roles
    for role, perm_names in ROLE_PERMISSIONS.items():
        print(f"Setting up permissions for role: {role}")
        for perm_name in perm_names:
            if perm_id := permissions.get(perm_name):
                role_perm = RolePermission(
                    role=role,
                    permission_id=perm_id
                )
                db.add(role_perm)
    
    await db.commit()
    print("Permission initialization complete!")

async def main():
    """Main function to run the permission initialization."""
    db = SessionLocal()
    try:
        await init_permissions(db)
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
