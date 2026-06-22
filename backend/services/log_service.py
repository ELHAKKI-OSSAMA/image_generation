from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, desc, asc, func, select
from sqlalchemy.future import select as async_select
from fastapi import HTTPException
from uuid import UUID

from schemas.log import Log, LogBase, LogFilter, LogSort, LogPagination, LogLevel, LogCategory
from schemas.response import PaginatedResponse

def _to_naive_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert timezone-aware datetime to naive UTC datetime"""
    if dt and dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt

class LogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(self, log_data: LogBase) -> Log:
        """Create a new log entry"""
        log_dict = log_data.dict()
        # Convert metadata to log_metadata for SQLAlchemy model
        if 'metadata' in log_dict:
            log_dict['log_metadata'] = log_dict.pop('metadata')
        
        db_log = Log(**log_dict)
        self.db.add(db_log)
        try:
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(db_log)
            return db_log
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create log: {str(e)}"
            )

    async def get_logs(
        self,
        filters: LogFilter,
        sort: LogSort,
        pagination: LogPagination
    ) -> PaginatedResponse:
        """Get logs with advanced filtering, sorting and pagination"""
        try:
            # Build base query
            stmt = async_select(Log)
            
            # Apply filters
            if filters.start_date:
                stmt = stmt.where(Log.timestamp >= _to_naive_datetime(filters.start_date))
            if filters.end_date:
                stmt = stmt.where(Log.timestamp <= _to_naive_datetime(filters.end_date))
            if filters.levels:
                stmt = stmt.where(Log.level.in_(filters.levels))
            if filters.categories:
                stmt = stmt.where(Log.category.in_(filters.categories))
            if filters.user_id:
                stmt = stmt.where(Log.user_id == filters.user_id)
            if filters.resource_type:
                stmt = stmt.where(Log.resource_type == filters.resource_type)
            if filters.resource_id:
                stmt = stmt.where(Log.resource_id == filters.resource_id)
            if filters.min_duration:
                stmt = stmt.where(Log.duration_ms >= filters.min_duration)
            if filters.status_code:
                stmt = stmt.where(Log.status_code == filters.status_code)
            if filters.search_query:
                search = f"%{filters.search_query}%"
                stmt = stmt.where(
                    or_(
                        Log.action.ilike(search),
                        Log.details.ilike(search),
                        Log.error_stack.ilike(search)
                    )
                )

            # Get total count
            count_stmt = select(func.count()).select_from(stmt.subquery())
            result = await self.db.execute(count_stmt)
            total_count = result.scalar()

            # Apply sorting
            if sort.order.lower() == "asc":
                stmt = stmt.order_by(asc(getattr(Log, sort.field)))
            else:
                stmt = stmt.order_by(desc(getattr(Log, sort.field)))

            # Apply pagination
            stmt = stmt.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)

            # Execute query
            result = await self.db.execute(stmt)
            logs = result.scalars().all()

            # Format logs for frontend
            formatted_logs = [
                {
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "level": log.level.value if hasattr(log.level, 'value') else log.level,
                    "category": log.category.value if hasattr(log.category, 'value') else log.category,
                    "action": log.action,
                    "user_id": str(log.user_id) if log.user_id else None,
                    "details": log.details,
                    "metadata": log.log_metadata if hasattr(log, 'log_metadata') else {}
                }
                for log in logs
            ]

            return PaginatedResponse(
                items=formatted_logs,
                total=total_count,
                page=pagination.page,
                limit=pagination.limit,
                pages=(total_count + pagination.limit - 1) // pagination.limit
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving logs: {str(e)}"
            )

    async def get_log_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive log statistics"""
        # Build base query
        stmt = async_select(Log)
        
        if start_date:
            stmt = stmt.where(Log.timestamp >= _to_naive_datetime(start_date))
        if end_date:
            stmt = stmt.where(Log.timestamp <= _to_naive_datetime(end_date))

        # Basic statistics
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.db.execute(count_stmt)
        total_logs = result.scalar()
        
        # Logs by level
        level_stmt = async_select(Log.level, func.count(Log.id)).group_by(Log.level)
        level_result = await self.db.execute(level_stmt)
        level_stats = level_result.all()
        logs_by_level = {level: count for level, count in level_stats}

        # Logs by category
        category_stmt = async_select(Log.category, func.count(Log.id)).group_by(Log.category)
        category_result = await self.db.execute(category_stmt)
        category_stats = category_result.all()
        logs_by_category = {category: count for category, count in category_stats}

        # Performance metrics
        perf_stmt = async_select(
            func.avg(Log.duration_ms).label('avg_duration'),
            func.min(Log.duration_ms).label('min_duration'),
            func.max(Log.duration_ms).label('max_duration')
        ).where(Log.duration_ms.isnot(None))
        perf_result = await self.db.execute(perf_stmt)
        performance_stats = perf_result.first()

        # Error analysis
        error_stmt = async_select(func.count()).where(Log.level == LogLevel.ERROR)
        error_result = await self.db.execute(error_stmt)
        error_count = error_result.scalar()
        error_rate = error_count / total_logs if total_logs > 0 else 0

        # Most common errors
        common_errors_stmt = async_select(
            Log.error_stack,
            func.count(Log.id).label('count')
        ).where(
            Log.error_stack.isnot(None)
        ).group_by(
            Log.error_stack
        ).order_by(
            desc('count')
        ).limit(10)
        common_errors_result = await self.db.execute(common_errors_stmt)
        common_errors = common_errors_result.all()

        # Busiest endpoints
        endpoints_stmt = async_select(
            Log.action,
            func.count(Log.id).label('count')
        ).where(
            Log.category == LogCategory.API
        ).group_by(
            Log.action
        ).order_by(
            desc('count')
        ).limit(10)
        endpoints_result = await self.db.execute(endpoints_stmt)
        busy_endpoints = endpoints_result.all()

        # Active users
        users_stmt = async_select(
            Log.user_id,
            func.count(Log.id).label('count')
        ).where(
            Log.user_id.isnot(None)
        ).group_by(
            Log.user_id
        ).order_by(
            desc('count')
        ).limit(10)
        users_result = await self.db.execute(users_stmt)
        active_users = users_result.all()

        return {
            "total_logs": total_logs,
            "logs_by_level": logs_by_level,
            "logs_by_category": logs_by_category,
            "performance_metrics": {
                "average_duration": performance_stats.avg_duration if performance_stats else None,
                "min_duration": performance_stats.min_duration if performance_stats else None,
                "max_duration": performance_stats.max_duration if performance_stats else None
            },
            "error_analysis": {
                "error_count": error_count,
                "error_rate": error_rate,
                "common_errors": [
                    {"error": error, "count": count}
                    for error, count in common_errors
                ]
            },
            "busy_endpoints": [
                {"endpoint": endpoint, "count": count}
                for endpoint, count in busy_endpoints
            ],
            "active_users": [
                {"user_id": user_id, "activity_count": count}
                for user_id, count in active_users
            ]
        }

    async def cleanup_logs(
        self,
        older_than: datetime,
        categories: Optional[List[LogCategory]] = None
    ) -> int:
        """Clean up old logs"""
        stmt = async_select(Log).where(Log.timestamp < _to_naive_datetime(older_than))
        
        if categories:
            stmt = stmt.where(Log.category.in_(categories))
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.db.execute(count_stmt)
        count = result.scalar()

        delete_stmt = stmt.delete()
        await self.db.execute(delete_stmt)
        await self.db.commit()
        
        return count
