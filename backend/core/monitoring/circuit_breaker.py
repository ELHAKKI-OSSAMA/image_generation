from typing import Callable, Any, Optional, Dict
from datetime import datetime, timedelta
import asyncio
from collections import deque
from fastapi import HTTPException, status

class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""
    pass

class CircuitBreakerState:
    """Circuit breaker state management."""
    
    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: int,
        half_open_timeout: int
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_timeout = half_open_timeout
        
        self.failures = deque(maxlen=failure_threshold)
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, or half-open
        self.last_state_change: datetime = datetime.utcnow()

    def record_failure(self) -> None:
        """Record a failure and update state if necessary."""
        now = datetime.utcnow()
        self.failures.append(now)
        self.last_failure_time = now
        
        if (
            len(self.failures) >= self.failure_threshold and
            self.state != "open"
        ):
            self.trip()

    def record_success(self) -> None:
        """Record a success and update state if necessary."""
        if self.state == "half-open":
            self.reset()
        self.failures.clear()

    def trip(self) -> None:
        """Trip the circuit breaker to open state."""
        self.state = "open"
        self.last_state_change = datetime.utcnow()

    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self.state = "closed"
        self.last_state_change = datetime.utcnow()
        self.failures.clear()

    def attempt_reset(self) -> None:
        """Attempt to reset to half-open state if recovery time has passed."""
        if self.state == "open":
            recovery_time = self.last_state_change + timedelta(seconds=self.recovery_timeout)
            if datetime.utcnow() >= recovery_time:
                self.state = "half-open"
                self.last_state_change = datetime.utcnow()

class OrganizationCircuitBreaker:
    """Circuit breaker implementation for organization operations."""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_timeout: int = 10
    ):
        """Initialize circuit breaker with configuration."""
        self.name = name
        self.state = CircuitBreakerState(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            half_open_timeout=half_open_timeout
        )
        self._fallback_handlers: Dict[str, Callable] = {}

    def register_fallback(
        self,
        operation: str,
        handler: Callable
    ) -> None:
        """Register a fallback handler for an operation."""
        self._fallback_handlers[operation] = handler

    async def execute(
        self,
        operation: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute an operation with circuit breaker protection."""
        self.state.attempt_reset()
        
        if self.state.state == "open":
            return await self._handle_open_state(operation)
            
        try:
            result = await func(*args, **kwargs)
            self.state.record_success()
            return result
            
        except Exception as e:
            self.state.record_failure()
            if self.state.state == "half-open":
                self.state.trip()
            return await self._handle_failure(operation, e)

    async def _handle_open_state(self, operation: str) -> Any:
        """Handle requests when circuit is open."""
        if fallback := self._fallback_handlers.get(operation):
            return await fallback()
            
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service {self.name} is currently unavailable"
        )

    async def _handle_failure(
        self,
        operation: str,
        error: Exception
    ) -> Any:
        """Handle operation failures."""
        if fallback := self._fallback_handlers.get(operation):
            return await fallback()
            
        raise error

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            "name": self.name,
            "state": self.state.state,
            "failure_count": len(self.state.failures),
            "last_failure": self.state.last_failure_time,
            "last_state_change": self.state.last_state_change
        }
