from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge
from fastapi import Depends
from datetime import datetime

from core.config import get_settings

class PerformanceMetrics:
    """Performance monitoring and metrics collection."""
    
    def __init__(self):
        """Initialize performance metrics collectors."""
        # Query metrics
        self.query_duration = Histogram(
            'organization_query_duration_seconds',
            'Duration of organization queries',
            ['query_name']
        )
        self.query_count = Counter(
            'organization_query_total',
            'Total number of organization queries',
            ['query_name']
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'organization_cache_hits_total',
            'Total number of cache hits',
            ['cache_type']
        )
        self.cache_misses = Counter(
            'organization_cache_misses_total',
            'Total number of cache misses',
            ['cache_type']
        )
        
        # Error metrics
        self.errors = Counter(
            'organization_errors_total',
            'Total number of errors',
            ['error_type']
        )
        
        # Performance gauges
        self.active_requests = Gauge(
            'organization_active_requests',
            'Number of active organization requests'
        )
        self.db_connections = Gauge(
            'organization_db_connections',
            'Number of active database connections'
        )

    def track_query(self, name: str, duration: float) -> None:
        """Track query execution time and count."""
        self.query_duration.labels(query_name=name).observe(duration)
        self.query_count.labels(query_name=name).inc()

    def track_cache(self, cache_type: str, hit: bool) -> None:
        """Track cache hits and misses."""
        if hit:
            self.cache_hits.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses.labels(cache_type=cache_type).inc()

    def track_error(self, error_type: str) -> None:
        """Track error occurrences."""
        self.errors.labels(error_type=error_type).inc()

    def track_request(self) -> None:
        """Track active request count."""
        self.active_requests.inc()

    def complete_request(self) -> None:
        """Decrement active request count."""
        self.active_requests.dec()

    def set_db_connections(self, count: int) -> None:
        """Set current database connection count."""
        self.db_connections.set(count)

    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect all current metrics."""
        return {
            "query_stats": {
                "total": self.query_count._value.sum(),
                "duration_avg": self.query_duration._sum.sum() / self.query_duration._count.sum()
            },
            "cache_stats": {
                "hits": self.cache_hits._value.sum(),
                "misses": self.cache_misses._value.sum(),
                "hit_ratio": self.cache_hits._value.sum() / (self.cache_hits._value.sum() + self.cache_misses._value.sum())
            },
            "error_stats": {
                "total": self.errors._value.sum()
            },
            "current_stats": {
                "active_requests": self.active_requests._value.get(),
                "db_connections": self.db_connections._value.get()
            }
        }
