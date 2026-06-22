from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Callable
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

from core.database import get_db
from database.models import Organization, UsageStatistic, OrganizationMember

class UsageTracker(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.tracked_paths = {
            "/api/v1/images/generate": "api_call",
            "/api/v1/images/upload": "storage",
            "/api/v1/events/create": "api_call"
        }
    
    async def get_organization_id(self, request: Request) -> uuid.UUID:
        """Extract organization ID from the request context"""
        try:
            # Get current user from request state
            user = getattr(request.state, "user", None)
            if isinstance(user, OrganizationMember):
                return user.organization_id
            return None
        except Exception:
            return None

    async def track_api_call(self, db: Session, organization_id: uuid.UUID):
        """Track API call usage"""
        today = datetime.utcnow().date()
        
        # Get or create today's usage statistic
        usage_stat = db.query(UsageStatistic).filter(
            UsageStatistic.organization_id == organization_id,
            UsageStatistic.date == today
        ).first()
        
        if not usage_stat:
            usage_stat = UsageStatistic(
                id=uuid.uuid4(),
                organization_id=organization_id,
                date=today
            )
            db.add(usage_stat)
        
        usage_stat.api_calls = (usage_stat.api_calls or 0) + 1
        db.commit()

    async def track_storage(self, db: Session, organization_id: uuid.UUID, bytes_used: int):
        """Track storage usage"""
        today = datetime.utcnow().date()
        
        # Get or create today's usage statistic
        usage_stat = db.query(UsageStatistic).filter(
            UsageStatistic.organization_id == organization_id,
            UsageStatistic.date == today
        ).first()
        
        if not usage_stat:
            usage_stat = UsageStatistic(
                id=uuid.uuid4(),
                organization_id=organization_id,
                date=today
            )
            db.add(usage_stat)
        
        usage_stat.storage_used_bytes = (usage_stat.storage_used_bytes or 0) + bytes_used
        db.commit()

    async def check_usage_limits(self, db: Session, organization_id: uuid.UUID) -> bool:
        """Check if organization has exceeded its usage limits"""
        organization = db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not organization:
            return False
        
        # Get current month's usage
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_usage = db.query(UsageStatistic).filter(
            UsageStatistic.organization_id == organization_id,
            UsageStatistic.date >= current_month_start
        ).all()
        
        # Calculate total usage
        total_api_calls = sum(stat.api_calls or 0 for stat in month_usage)
        total_storage_bytes = sum(stat.storage_used_bytes or 0 for stat in month_usage)
        total_storage_gb = total_storage_bytes / (1024 * 1024 * 1024)  # Convert to GB
        
        # Check limits
        if total_api_calls >= organization.max_api_calls_per_month:
            return False
        if total_storage_gb >= organization.max_storage_gb:
            return False
        
        return True

    async def dispatch(self, request: Request, call_next: Callable):
        """Middleware to track API usage"""
        # Skip tracking for non-API paths
        if not any(path in request.url.path for path in self.tracked_paths.keys()):
            return await call_next(request)
        
        # Get organization ID
        organization_id = await self.get_organization_id(request)
        if not organization_id:
            return await call_next(request)
        
        # Get database session
        db = next(get_db())
        
        try:
            # Check usage limits before processing
            if not await self.check_usage_limits(db, organization_id):
                return JSONResponse(
                    content={
                        "error": "Usage limit exceeded",
                        "detail": "You have exceeded your subscription plan limits"
                    },
                    status_code=429  # HTTP 429 Too Many Requests
                )
            
            # Process the request
            response = await call_next(request)
            
            # Track usage based on path
            path = request.url.path
            if path in self.tracked_paths:
                usage_type = self.tracked_paths[path]
                
                if usage_type == "api_call":
                    await self.track_api_call(db, organization_id)
                elif usage_type == "storage" and hasattr(request.state, "uploaded_bytes"):
                    await self.track_storage(db, organization_id, request.state.uploaded_bytes)
            
            return response
            
        except Exception as e:
            # Log the error but don't block the request
            print(f"Error tracking usage: {str(e)}")
            return await call_next(request)
        finally:
            db.close()
