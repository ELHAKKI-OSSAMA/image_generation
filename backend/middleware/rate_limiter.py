from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Tuple
import time
from fastapi.responses import JSONResponse 

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limits: Dict[str, Dict[str, Tuple[int, float]]] = {
            # endpoint: {ip: (count, start_time)}
            "login": {},
            "register": {},
            "forgot-password": {},
            "api": {}  # general API rate limit
        }
        self.limits = {
            "login": (50, 300),  # 5 attempts per 5 minutes
            "register": (50, 3600),  # 3 attempts per hour
            "forgot-password": (50, 86400),  # 3 attempts per 24 hours
            "api": (300, 60)  # 100 requests per minute
        }
        
        # Endpoints that are exempt from rate limiting
        self.exempt_endpoints = {
            "/api/v1/auth/refresh",  # Token refresh endpoint
            "/api/v1/auth/logout",    # Logout endpoint
            "/api/v1/admin"            # Admin endpoints
        }
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_limits())

    async def _cleanup_expired_limits(self):
        """Periodically clean up expired rate limits"""
        while True:
            current_time = time.time()
            for endpoint in self.rate_limits:
                limit_duration = self.limits[endpoint][1]
                self.rate_limits[endpoint] = {
                    ip: (count, start_time)
                    for ip, (count, start_time) in self.rate_limits[endpoint].items()
                    if current_time - start_time < limit_duration
                }
            await asyncio.sleep(60)  # Run cleanup every minute

    def _get_endpoint_type(self, path: str) -> str:
        """Determine the type of endpoint for rate limiting"""
        if "/auth/login" in path:
            return "login"
        elif "/auth/register" in path:
            return "register"
        elif "/auth/forgot-password" in path:
            return "forgot-password"
        return "api"

    def _is_rate_limited(self, endpoint_type: str, ip: str, request: Request) -> bool:
        """Check if the request should be rate limited"""
        # Skip rate limiting for admin endpoints
        if request.url.path.startswith("/api/v1/admin"):
            return False
            
        current_time = time.time()
        endpoint_limits = self.rate_limits.get(endpoint_type, {})
        max_requests, window = self.limits[endpoint_type]

        # Use user ID for authenticated users, IP for unauthenticated
        tracking_id = request.state.user.id if hasattr(request.state, "user") and request.state.user else ip

        if tracking_id in endpoint_limits:
            count, start_time = endpoint_limits[tracking_id]
            if current_time - start_time >= window:
                # Reset if window has passed
                endpoint_limits[tracking_id] = (1, current_time)
                return False
            elif count >= max_requests:
                return True
            else:
                # Increment count
                endpoint_limits[tracking_id] = (count + 1, start_time)
                return False
        else:
            # First request from this user/IP
            endpoint_limits[tracking_id] = (1, current_time)
            self.rate_limits[endpoint_type] = endpoint_limits
            return False

    async def dispatch(self, request: Request, call_next):
        """Handle the request and apply rate limiting"""
        # Skip rate limiting for exempt endpoints
        if request.url.path in self.exempt_endpoints:
            return await call_next(request)
            
        # Get client IP
        client_ip = (
    request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    or (request.client.host if request.client else "unknown")
)
        
        # Determine endpoint type
        endpoint_type = self._get_endpoint_type(request.url.path)
        print(f"Rate limiting endpoint: {request.url.path} as type: {endpoint_type}") 
        # Check rate limit
        if self._is_rate_limited(endpoint_type, client_ip, request):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "message": "Too many requests",
                    "retry_after": self.limits[endpoint_type][1],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Process the request
        response = await call_next(request)
        return response
