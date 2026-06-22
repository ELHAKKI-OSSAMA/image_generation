from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..dependencies import get_current_user
from ..services.log_analytics_service import LogAnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/error-trends")
async def get_error_trends(
    timeframe: str = "24h",
    interval: str = "1h",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get error trends analysis"""
    analytics_service = LogAnalyticsService(db)
    return await analytics_service.get_error_trends(timeframe, interval)

@router.get("/performance")
async def get_performance_metrics(
    timeframe: str = "24h",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get API performance metrics"""
    analytics_service = LogAnalyticsService(db)
    return await analytics_service.get_performance_metrics(timeframe)

@router.get("/anomalies")
async def detect_anomalies(
    sensitivity: float = 2.0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Detect anomalies in log patterns"""
    analytics_service = LogAnalyticsService(db)
    return await analytics_service.detect_anomalies(sensitivity)

@router.get("/user-activity")
async def get_user_activity(
    timeframe: str = "24h",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user activity analysis"""
    analytics_service = LogAnalyticsService(db)
    return await analytics_service.get_user_activity(timeframe)

@router.get("/security")
async def get_security_analysis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get security events analysis"""
    analytics_service = LogAnalyticsService(db)
    return await analytics_service.get_security_analysis()
