from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import datetime, timedelta
from math import ceil

from core.database import get_db
from core.security import get_current_user
from database.models import Admin, OrganizationMember
from database.models.enums import UserRole, AdminPermission
from schemas.log import LogBase, LogFilter, LogSort, LogPagination, LogLevel, LogCategory
from services.log_service import LogService

router = APIRouter( prefix="/logs",tags=["logs"])

@router.post("/", response_model=LogBase)
async def create_log(
    log: LogBase,
    db: Session = Depends(get_db),
    current_user: Union[Admin, OrganizationMember] = Depends(get_current_user)
):
    """Create a new log entry"""
    log_service = LogService(db)
    return await log_service.create_log(log)

@router.get("/")
async def get_logs(
    start_date: Optional[datetime] = Query(None, description="Filter logs from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter logs until this date"),
    level: Optional[str] = Query(None, description="Filter by log level (INFO, WARNING, ERROR)"),
    category: Optional[str] = Query(None, description="Filter by category (AUTH, USER, ADMIN, SYSTEM)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: Union[Admin, OrganizationMember] = Depends(get_current_user)
):
    """
    Get system logs with filtering and pagination.
    Only accessible by SUPER_ADMIN or ADMIN with VIEW_AUDIT_LOGS permission.
    """
    # 1. Permission Check
    if not (
        current_user.role == UserRole.SUPER_ADMIN or 
        (current_user.role == UserRole.ADMIN and AdminPermission.VIEW_AUDIT_LOGS in current_user.permissions)
    ):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view system logs"
        )

    # 2. Initialize Log Service
    log_service = LogService(db)

    try:
        # 3. Prepare Filters
        filters = LogFilter(
            start_date=start_date,
            end_date=end_date,
            level=[level.upper()] if level else None,
            category=[category.upper()] if category else None
        )

        # 4. Get Logs
        result = await log_service.get_logs(
            filters=filters,
            sort=LogSort(field="timestamp", ascending=False),
            pagination=LogPagination(page=page, limit=limit)
        )

        # 5. Format Response for Frontend
        formatted_logs = [
            {
                "timestamp": log.created_at.isoformat(),
                "level": log.level if hasattr(log, 'level') else 'INFO',
                "category": log.category if hasattr(log, 'category') else log.resource_type,
                "action": log.action,
                "user_id": str(log.user_id) if log.user_id else None,
                "details": log.details,
                "metadata": log.event_data if hasattr(log, 'event_data') else {}
            }
            for log in result.items
        ]

        # 6. Return Paginated Response
        return {
            "items": formatted_logs,
            "total": result.total,
            "page": page,
            "limit": limit,
            "pages": ceil(result.total / limit)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving logs: {str(e)}"
        )

@router.get("/statistics")
async def get_log_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Union[Admin, OrganizationMember] = Depends(get_current_user)
):
    """Get comprehensive log statistics"""
    log_service = LogService(db)
    return await log_service.get_log_statistics(start_date, end_date)

@router.delete("/cleanup")
async def cleanup_logs(
    older_than: datetime,
    categories: Optional[List[LogCategory]] = Query(None),
    db: Session = Depends(get_db),
    current_user: Union[Admin, OrganizationMember] = Depends(get_current_user)
):
    """Clean up old logs"""
    log_service = LogService(db)
    deleted_count = await log_service.cleanup_logs(older_than, categories)
    return {"message": f"Successfully deleted {deleted_count} logs"}

# WebSocket for real-time log streaming
class LogConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.disconnect(connection)

manager = LogConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time log streaming"""
    try:
        # Verify token and get user
        current_user = await get_current_user(token, db)
        await manager.connect(websocket)
        
        try:
            while True:
                # Wait for new logs and broadcast them
                data = await websocket.receive_text()
                await manager.broadcast({"message": data})
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    except Exception as e:
        await websocket.close(code=1008, reason=str(e))

# Middleware to automatically log API requests
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get request details
        path = request.url.path
        method = request.method
        headers = dict(request.headers)
        client_ip = request.client.host
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = int((time.time() - start_time) * 1000)
            
            # Create log entry
            log_data = LogBase(
                level=LogLevel.INFO,
                category=LogCategory.API,
                action=f"{method} {path}",
                status_code=response.status_code,
                duration_ms=duration,
                ip_address=client_ip,
                metadata={
                    "headers": headers,
                    "query_params": dict(request.query_params)
                }
            )
            
            # Log asynchronously
            await create_log(log_data, request.state.db)
            
            return response
        except Exception as e:
            # Log error
            log_data = LogBase(
                level=LogLevel.ERROR,
                category=LogCategory.API,
                action=f"{method} {path}",
                error_stack=str(e),
                ip_address=client_ip
            )
            
            await create_log(log_data, request.state.db)
            raise
