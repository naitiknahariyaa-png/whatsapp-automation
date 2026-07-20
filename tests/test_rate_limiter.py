"""
🧪 Rate Limiter Tests
====================
Test rate limiter functionality.
"""

import pytest
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.rate_limiter.limiter import RateLimiter, RateLimitResult
except ImportError:
    pytest.skip("Rate limiter not available", allow_module_level=True)


class TestRateLimiter:
    """Test cases for RateLimiter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.limiter = RateLimiter(requests_per_minute=10, requests_per_hour=100)
    
    def test_first_request_allowed(self):
        """Test first request is always allowed."""
        result = self.limiter.check("user1")
        assert result.allowed is True
        assert result.remaining == 9  # 10 - 1
    
    def test_multiple_requests_within_limit(self):
        """Test multiple requests within limit."""
        for i in range(5):
            result = self.limiter.check(f"user2")
            assert result.allowed is True
        assert result.remaining == 4  # 10 - 5
    
    def test_limit_exceeded(self):
        """Test limit is enforced."""
        # Make 10 requests (at limit)
        for _ in range(10):
            self.limiter.check("user3")
        
        # Next should be denied
        result = self.limiter.check("user3")
        assert result.allowed is False
        assert result.retry_after is not None
    
    def test_different_users_separate_limits(self):
        """Test different users have separate limits."""
        # User A uses 5 requests
        for _ in range(5):
            self.limiter.check("userA")
        
        # User B should still have full limit
        result = self.limiter.check("userB")
        assert result.allowed is True
        assert result.remaining == 9
    
    def test_reset_clears_limits(self):
        """Test reset clears limits for user."""
        # Use some requests
        for _ in range(5):
            self.limiter.check("userD")
        
        # Reset
        self.limiter.reset("userD")
        
        # Should have full limit again
        result = self.limiter.check("userD")
        assert result.allowed is True
        assert result.remaining == 9
    
    def test_get_status(self):
        """Test status reporting."""
        for _ in range(3):
            self.limiter.check("userE")
        
        status = self.limiter.get_status("userE")
        assert status['minute_used'] == 3
        assert status['minute_remaining'] == 7
        assert status['hour_used'] == 3
        assert status['hour_remaining'] == 97


class TestRateLimitResult:
    """Test cases for RateLimitResult."""
    
    def test_result_dataclass(self):
        """Test result dataclass."""
        result = RateLimitResult(
            allowed=True,
            remaining=5,
            reset_at=1000.0
        )
        assert result.allowed is True
        assert result.remaining == 5
        assert result.reset_at == 1000.0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
