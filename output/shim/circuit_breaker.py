"""Circuit breaker pattern implementation for fault tolerance"""
import time
import logging
from enum import Enum
from typing import Callable, Any

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # Normal operation - requests go through
    OPEN = "open"              # Service unavailable - use fallback
    HALF_OPEN = "half_open"    # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    
    Prevents cascading failures when payment service is down by:
    1. Tracking failure count
    2. Opening circuit after threshold failures
    3. Automatically attempting recovery after timeout
    4. Using fallback when circuit is open
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery
            success_threshold: Successful calls needed to close circuit from half-open
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
        logger.info(
            f"Circuit breaker initialized: "
            f"failure_threshold={failure_threshold}, "
            f"timeout={timeout}s, "
            f"success_threshold={success_threshold}"
        )
    
    def call(
        self,
        func: Callable,
        fallback: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Primary function to call (payment service)
            fallback: Fallback function (legacy payment logic)
            *args: Positional arguments for functions
            **kwargs: Keyword arguments for functions
            
        Returns:
            Result from either primary function or fallback
        """
        # Check if circuit should attempt reset
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info("Circuit breaker: Attempting reset (HALF_OPEN)")
                self.state = CircuitState.HALF_OPEN
            else:
                # Circuit is open, use fallback immediately
                logger.warning(
                    f"Circuit breaker OPEN: Using fallback "
                    f"(failures={self.failure_count})"
                )
                return fallback(*args, **kwargs)
        
        # Try primary function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            logger.error(f"Circuit breaker: Primary function failed: {e}")
            self._on_failure()
            
            # If circuit just opened, use fallback
            if self.state == CircuitState.OPEN:
                logger.warning("Circuit breaker: Circuit OPENED, using fallback")
                return fallback(*args, **kwargs)
            else:
                # Circuit still closed or half-open, propagate exception
                raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.info(
                f"Circuit breaker HALF_OPEN: Success {self.success_count}/"
                f"{self.success_threshold}"
            )
            
            if self.success_count >= self.success_threshold:
                logger.info("Circuit breaker: Circuit CLOSED (service recovered)")
                self.state = CircuitState.CLOSED
                self.success_count = 0
        
        elif self.state == CircuitState.CLOSED:
            # Normal operation
            pass
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        logger.warning(
            f"Circuit breaker: Failure {self.failure_count}/"
            f"{self.failure_threshold}"
        )
        
        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.error(
                    f"Circuit breaker: Opening circuit after "
                    f"{self.failure_count} failures"
                )
                self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """
        Check if enough time has passed to attempt reset
        
        Returns:
            True if should attempt reset, False otherwise
        """
        if not self.last_failure_time:
            return False
        
        elapsed = time.time() - self.last_failure_time
        should_reset = elapsed >= self.timeout
        
        if should_reset:
            logger.info(
                f"Circuit breaker: {elapsed:.1f}s elapsed since last failure, "
                f"attempting reset"
            )
        
        return should_reset
    
    def get_state(self) -> str:
        """Get current circuit state"""
        return self.state.value
    
    def get_stats(self) -> dict:
        """
        Get circuit breaker statistics
        
        Returns:
            Dictionary with current stats
        """
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "time_since_failure": (
                time.time() - self.last_failure_time
                if self.last_failure_time
                else None
            )
        }
    
    def reset(self):
        """Manually reset circuit breaker"""
        logger.info("Circuit breaker: Manual reset")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

# Made with Bob
