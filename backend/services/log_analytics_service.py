from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.orm import Session
import numpy as np
from scipy import stats
from collections import defaultdict

from ..models.log import Log, LogLevel, LogCategory

class LogAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_error_trends(
        self,
        timeframe: str = "24h",
        interval: str = "1h"
    ) -> Dict[str, Any]:
        """Analyze error patterns over time"""
        # Convert timeframe to timedelta
        timeframe_map = {
            "1h": timedelta(hours=1),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        interval_map = {
            "5m": timedelta(minutes=5),
            "1h": timedelta(hours=1),
            "1d": timedelta(days=1)
        }

        end_time = datetime.utcnow()
        start_time = end_time - timeframe_map.get(timeframe, timeframe_map["24h"])
        interval_delta = interval_map.get(interval, interval_map["1h"])

        # Query error logs in the timeframe
        query = self.db.query(
            func.date_trunc('hour', Log.timestamp).label('time_bucket'),
            Log.level,
            func.count(Log.id).label('count')
        ).filter(
            Log.timestamp.between(start_time, end_time),
            Log.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
        ).group_by(
            'time_bucket',
            Log.level
        ).order_by('time_bucket')

        results = await query.all()

        # Process results
        trends = defaultdict(list)
        current_time = start_time
        while current_time <= end_time:
            bucket_data = {
                'timestamp': current_time,
                'error_count': 0,
                'critical_count': 0
            }
            
            for result in results:
                if result.time_bucket == current_time:
                    if result.level == LogLevel.ERROR:
                        bucket_data['error_count'] = result.count
                    else:
                        bucket_data['critical_count'] = result.count
            
            trends['data'].append(bucket_data)
            current_time += interval_delta

        return {
            'timeframe': timeframe,
            'interval': interval,
            'trends': trends
        }

    async def get_performance_metrics(
        self,
        timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """Calculate detailed API performance metrics"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        # Query performance data
        query = self.db.query(
            Log.action,
            func.count(Log.id).label('total_requests'),
            func.avg(Log.duration_ms).label('avg_duration'),
            func.min(Log.duration_ms).label('min_duration'),
            func.max(Log.duration_ms).label('max_duration'),
            func.percentile_cont(0.95).within_group(
                Log.duration_ms.desc()
            ).label('p95_duration')
        ).filter(
            Log.timestamp.between(start_time, end_time),
            Log.category == LogCategory.API,
            Log.duration_ms.isnot(None)
        ).group_by(Log.action)

        results = await query.all()

        # Calculate statistics
        metrics = []
        for result in results:
            metrics.append({
                'endpoint': result.action,
                'total_requests': result.total_requests,
                'avg_duration_ms': round(result.avg_duration, 2),
                'min_duration_ms': result.min_duration,
                'max_duration_ms': result.max_duration,
                'p95_duration_ms': round(result.p95_duration, 2)
            })

        return {
            'timeframe': timeframe,
            'metrics': sorted(metrics, key=lambda x: x['avg_duration_ms'], reverse=True)
        }

    async def detect_anomalies(
        self,
        sensitivity: float = 2.0
    ) -> Dict[str, Any]:
        """Detect unusual patterns in logs using statistical analysis"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)

        # Query hourly error counts
        query = self.db.query(
            func.date_trunc('hour', Log.timestamp).label('hour'),
            func.count(Log.id).label('error_count')
        ).filter(
            Log.timestamp.between(start_time, end_time),
            Log.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
        ).group_by('hour').order_by('hour')

        results = await query.all()

        # Prepare data for analysis
        timestamps = [r.hour for r in results]
        counts = [r.error_count for r in results]

        if not counts:
            return {'anomalies': []}

        # Calculate Z-scores
        mean = np.mean(counts)
        std = np.std(counts)
        z_scores = stats.zscore(counts) if len(counts) > 1 else [0]

        # Detect anomalies
        anomalies = []
        for i, (timestamp, count, z_score) in enumerate(zip(timestamps, counts, z_scores)):
            if abs(z_score) > sensitivity:
                # Get related errors
                error_details = await self.db.query(
                    Log.error_stack,
                    func.count(Log.id).label('count')
                ).filter(
                    Log.timestamp.between(
                        timestamp,
                        timestamp + timedelta(hours=1)
                    ),
                    Log.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
                ).group_by(Log.error_stack).order_by(desc('count')).limit(3).all()

                anomalies.append({
                    'timestamp': timestamp,
                    'error_count': count,
                    'z_score': round(float(z_score), 2),
                    'deviation_from_mean': round(count - mean, 2),
                    'top_errors': [
                        {'error': e.error_stack, 'count': e.count}
                        for e in error_details
                    ]
                })

        return {
            'anomalies': sorted(anomalies, key=lambda x: abs(x['z_score']), reverse=True),
            'analysis_period': {
                'start': start_time,
                'end': end_time
            },
            'statistics': {
                'mean_errors_per_hour': round(mean, 2),
                'std_deviation': round(std, 2),
                'sensitivity_threshold': sensitivity
            }
        }

    async def get_user_activity(
        self,
        timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)

        # Get user sessions
        session_query = self.db.query(
            Log.user_id,
            func.count(distinct(Log.session_id)).label('session_count'),
            func.count(Log.id).label('action_count'),
            func.avg(Log.duration_ms).label('avg_response_time')
        ).filter(
            Log.timestamp.between(start_time, end_time),
            Log.user_id.isnot(None)
        ).group_by(Log.user_id)

        sessions = await session_query.all()

        # Get most used features
        feature_query = self.db.query(
            Log.user_id,
            Log.action,
            func.count(Log.id).label('count')
        ).filter(
            Log.timestamp.between(start_time, end_time),
            Log.user_id.isnot(None)
        ).group_by(
            Log.user_id,
            Log.action
        ).order_by(desc('count'))

        features = await feature_query.all()

        # Process results
        user_activity = defaultdict(lambda: {
            'session_count': 0,
            'action_count': 0,
            'avg_response_time': 0,
            'top_actions': []
        })

        for session in sessions:
            user_activity[session.user_id].update({
                'session_count': session.session_count,
                'action_count': session.action_count,
                'avg_response_time': round(session.avg_response_time, 2)
            })

        for feature in features:
            if len(user_activity[feature.user_id]['top_actions']) < 5:
                user_activity[feature.user_id]['top_actions'].append({
                    'action': feature.action,
                    'count': feature.count
                })

        return {
            'timeframe': timeframe,
            'user_activity': [
                {
                    'user_id': user_id,
                    **activity
                }
                for user_id, activity in user_activity.items()
            ]
        }

    async def get_security_analysis(self) -> Dict[str, Any]:
        """Analyze security-related events"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)

        # Get security events
        security_query = self.db.query(
            Log.action,
            Log.ip_address,
            func.count(Log.id).label('attempt_count')
        ).filter(
            Log.timestamp.between(start_time, end_time),
            Log.category == LogCategory.SECURITY
        ).group_by(
            Log.action,
            Log.ip_address
        ).having(
            func.count(Log.id) > 10  # Threshold for suspicious activity
        ).order_by(desc('attempt_count'))

        security_events = await security_query.all()

        # Process results
        suspicious_activity = []
        for event in security_events:
            suspicious_activity.append({
                'action': event.action,
                'ip_address': event.ip_address,
                'attempt_count': event.attempt_count
            })

        return {
            'analysis_period': {
                'start': start_time,
                'end': end_time
            },
            'suspicious_activity': suspicious_activity
        }
