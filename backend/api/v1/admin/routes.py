from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime, timedelta, timezone

from core.database import get_db
from api.v1.auth.dependencies import get_current_admin, get_current_user
from database.models.enums import UserRole
from services.admin_service import AdminService
from schemas.auth import UserResponse
from schemas.organization import OrganizationResponse
from database.models import User, UsageStatistic
from database.models.enums import VerificationStatus as UserStatus, OrganizationStatus

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/organizations", response_model=List[OrganizationResponse])
async def list_organizations(
    status: OrganizationStatus = OrganizationStatus.PENDING,  # Default to pending
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List organizations with optional status filter"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can list organizations")
    admin_service = AdminService(db)
    organizations = await admin_service.list_organizations(status)
    return organizations

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    status: UserStatus = None,
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can list users")
    admin_service = AdminService(db)
    users = await admin_service.list_users(status)
    return users

@router.post("/approve-org/{id}")
async def approve_organization(
    id: UUID,
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),

    db: AsyncSession = Depends(get_db)
):
    """Approve an organization"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can approve organizations")
    admin_service = AdminService(db)
    await admin_service.approve_organization(id, current_admin.id)
    return {"message": "Organization approved successfully"}

@router.post("/suspend-org/{id}")
async def suspend_organization(
    id: UUID,
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),

    db: AsyncSession = Depends(get_db)
):
    """Suspend an organization"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can suspend organizations")
    admin_service = AdminService(db)
    await admin_service.suspend_organization(id)
    return {"message": "Organization suspended successfully"}

@router.post("/suspend-user/{id}")
async def suspend_user(
    id: UUID,
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Suspend a user"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can suspend users")
    admin_service = AdminService(db)
    await admin_service.suspend_user(id)
    return {"message": "User suspended successfully"}

@router.post("/restore-user/{id}")
async def restore_user(
    id: UUID,
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Restore a suspended user"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can restore users")
    admin_service = AdminService(db)
    await admin_service.restore_user(id)
    return {"message": "User restored successfully"}

@router.get("/stats")
async def get_system_stats(
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),

    db: AsyncSession = Depends(get_db)
):
    """Get system-wide statistics"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can get system statistics")
    admin_service = AdminService(db)
    
    # Get user and organization stats
    users = await admin_service.list_users()
    orgs = await admin_service.list_organizations()
    active_orgs = [org for org in orgs if org.status == OrganizationStatus.active]
    
    # Get new users in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users = [user for user in users if user.created_at and user.created_at >= week_ago]

    stats = {
        "user_stats": {
            "total": len(users),
            "new_this_week": len(new_users)
        },
        "org_stats": {
            "total": len(orgs),
            "active": len(active_orgs)
        },
        "system_stats": {
            "gpu_metrics": None,  # Not implemented
            "storage_metrics": None,  # Not implemented
            "image_metrics": None  # Not implemented
        },
        "last_updated": datetime.utcnow().isoformat()
    }
    
    return stats

@router.get("/stats/users")
async def get_user_stats(
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),

    db: AsyncSession = Depends(get_db)
):
    """Get user statistics"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can get user statistics")
    admin_service = AdminService(db)
    users = await admin_service.list_users()
    
    stats = {
        "total": len(users),
        "active": len([u for u in users if u.status == UserStatus.VERIFIED]),
        "pending": len([u for u in users if u.status == UserStatus.PENDING])
    }
    
    return stats

@router.get("/stats/organizations")
async def get_organization_stats(
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),

    db: AsyncSession = Depends(get_db)
):
    """Get organization statistics"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can get organization statistics")
    admin_service = AdminService(db)
    organizations = await admin_service.list_organizations()
    
    stats = {
        "total": len(organizations),
        "active": len([o for o in organizations if o.status == OrganizationStatus.ACTIVE]),
        "pending": len([o for o in organizations if o.status == OrganizationStatus.PENDING])
    }
    
    return stats

@router.get("/stats/trends")
async def get_trends(
    start: datetime = Query(..., description="Start datetime for the trend data"),
    end: datetime = Query(..., description="End datetime for the trend data"),
    current_admin: User = Depends(get_current_admin),
    current_user: User = Depends(get_current_user),

    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can get trend data")
    print("\n=== Debug: /stats/trends endpoint ===")
    print(f"Received parameters - start: {start} ({type(start)}), end: {end} ({type(end)})")
    print(f"Current admin: {current_admin.email if current_admin else 'None'}")
    """Get trend data for users, organizations, and system metrics"""
    admin_service = AdminService(db)
    
    # Ensure both dates are timezone-aware
    print("\nBefore timezone adjustment:")
    print(f"start.tzinfo: {start.tzinfo}")
    print(f"end.tzinfo: {end.tzinfo}")
    
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
        
    print("\nAfter timezone adjustment:")
    print(f"start: {start}")
    print(f"end: {end}")
    
    # Get user trends
    time_bucket = func.date_trunc('hour', User.created_at.op('AT TIME ZONE')('UTC')).label('time')
    stmt = select(
        time_bucket,
        func.count().label('count')
    ).where(
        User.created_at.between(
            func.timezone('UTC', start),
            func.timezone('UTC', end)
        )
    ).group_by(
        time_bucket
    ).order_by(
        time_bucket
    )
    
    result = await db.execute(stmt)
    user_trends = result.all()
    print("\nUser trends query results:")
    print(f"Number of user trend records: {len(user_trends)}")
    print(f"Sample record: {user_trends[0] if user_trends else 'No records'}")
    
    # Get API usage trends
    time_bucket = func.date_trunc('hour', UsageStatistic.timestamp.op('AT TIME ZONE')('UTC')).label('time')
    stmt = select(
        time_bucket,
        func.count().label('count')
    ).where(
        UsageStatistic.timestamp.between(
            func.timezone('UTC', start),
            func.timezone('UTC', end)
        )
    ).group_by(
        time_bucket
    ).order_by(
        time_bucket
    )
    
    result = await db.execute(stmt)
    api_trends = result.all()
    print("\nAPI usage trends query results:")
    print(f"Number of API trend records: {len(api_trends)}")
    print(f"Sample record: {api_trends[0] if api_trends else 'No records'}")
    
    # Get performance metrics
    time_bucket = func.date_trunc('hour', UsageStatistic.timestamp.op('AT TIME ZONE')('UTC')).label('time')
    stmt = select(
        time_bucket,
        func.avg(UsageStatistic.response_time).label('avg_response_time')
    ).where(
        UsageStatistic.timestamp.between(
            func.timezone('UTC', start),
            func.timezone('UTC', end)
        )
    ).group_by(
        time_bucket
    ).order_by(
        time_bucket
    )
    
    result = await db.execute(stmt)
    performance_trends = result.all()
    print("\nPerformance trends query results:")
    print(f"Number of performance records: {len(performance_trends)}")
    print(f"Sample record: {performance_trends[0] if performance_trends else 'No records'}")
    print("\n=== End debug logs ===\n")
    
    return {
        "user_activity": [
            {"time": t.time.isoformat(), "count": t.count}
            for t in user_trends
        ],
        "api_usage": [
            {"time": t.time.isoformat(), "count": t.count}
            for t in api_trends
        ],
        "performance": [
            {"time": t.time.isoformat(), "avg_response_time": float(t.avg_response_time)}
            for t in performance_trends
        ]
    }

@router.get("/stats/daily")
async def get_daily_stats(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's statistics"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can get daily statistics")
    today = datetime.utcnow().date()
    admin_service = AdminService(db)
    
    # Get today's new users
    stmt = select(func.count()).select_from(User).where(
        func.date(User.created_at) == today
    )
    result = await db.execute(stmt)
    new_users_today = result.scalar()
    
    # Get today's API calls
    stmt = select(func.count()).select_from(UsageStatistic).where(
        func.date(UsageStatistic.timestamp) == today
    )
    result = await db.execute(stmt)
    api_calls_today = result.scalar()
    
    # Get average response time today
    stmt = select(func.avg(UsageStatistic.response_time)).select_from(UsageStatistic).where(
        func.date(UsageStatistic.timestamp) == today
    )
    result = await db.execute(stmt)
    avg_response_time = result.scalar()
    
    return {
        "new_users": new_users_today,
        "api_calls": api_calls_today,
        "avg_response_time": float(avg_response_time) if avg_response_time else None,
        "date": str(today)
    }

@router.get("/system-logs")
async def get_system_logs(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """Get recent system logs"""
    if current_user.role != UserRole.SUPER_ADMIN :
        raise HTTPException(403, "Only super admin can get system logs")
    from database.models.audit import AuditLog
    
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return {
        "logs": [
            {
                "id": str(log.id),
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "action": log.action,
                "category": log.category,
                "details": log.details,
                "user_id": str(log.user_id) if log.user_id else None,
                "metadata": log.event_data
            } for log in logs
        ]
    }
