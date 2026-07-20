"""
⏱️ Rate Limiter Module
====================
Prevents abuse by limiting request rates per user/IP.
"""

import time
from typing import Dict, Optional
from collections import defaultdict
from dataclasses import dataclass
import threading


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    remaining: int
    reset_at: float
    retry_after: Optional[int] = None


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Usage:
        limiter = RateLimiter(requests_per_minute=60)
        
        if limiter.check("user123"):
            # Process request
        else:
            # Rate limited
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        
        # Track requests: {key: [(timestamp, count), ...]}
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
        
        self._lock = threading.Lock()
    
    def _clean_old_requests(self, timestamps: list, window: float) -> None:
        """Remove requests outside the time window."""
        current_time = time.time()
        return [t for t in timestamps if current_time - t < window]
    
    def check(self, key: str) -> RateLimitResult:
        """
        Check if request is allowed.
        
        Args:
            key: Unique identifier (user ID, IP, etc.)
            
        Returns:
            RateLimitResult with allowance info
        """
        with self._lock:
            current_time = time.time()
            
            # Clean old requests
            self.minute_requests[key] = self._clean_old_requests(
                self.minute_requests[key], 60
            )
            self.hour_requests[key] = self._clean_old_requests(
                self.hour_requests[key], 3600
            )
            
            # Check minute limit
            minute_count = len(self.minute_requests[key])
            if minute_count >= self.requests_per_minute:
                oldest = min(self.minute_requests[key])
                retry_after = int(60 - (current_time - oldest))
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=current_time + retry_after,
                    retry_after=retry_after
                )
            
            # Check hour limit
            hour_count = len(self.hour_requests[key])
            if hour_count >= self.requests_per_hour:
                oldest = min(self.hour_requests[key])
                retry_after = int(3600 - (current_time - oldest))
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=current_time + retry_after,
                    retry_after=retry_after
                )
            
            # Record this request
            self.minute_requests[key].append(current_time)
            self.hour_requests[key].append(current_time)
            
            return RateLimitResult(
                allowed=True,
                remaining=self.requests_per_minute - minute_count - 1,
                reset_at=current_time + 60
            )
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        with self._lock:
            self.minute_requests.pop(key, None)
            self.hour_requests.pop(key, None)
    
    def get_status(self, key: str) -> Dict:
        """Get current rate limit status."""
        with self._lock:
            current_time = time.time()
            
            self.minute_requests[key] = self._clean_old_requests(
                self.minute_requests[key], 60
            )
            self.hour_requests[key] = self._clean_old_requests(
                self.hour_requests[key], 3600
            )
            
            return {
                'minute_used': len(self.minute_requests[key]),
                'minute_limit': self.requests_per_minute,
                'minute_remaining': self.requests_per_minute - len(self.minute_requests[key]),
                'hour_used': len(self.hour_requests[key]),
                'hour_limit': self.requests_per_hour,
                'hour_remaining': self.requests_per_hour - len(self.hour_requests[key]),
            }


# Default limiter instance
default_limiter = RateLimiter()
