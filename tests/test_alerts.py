"""
====================================================================
TEST ALERTS MODULE
====================================================================
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSendAlert:
    """Test send_alert function"""
    
    def test_alert_function_exists(self):
        """Test that send_alert function exists"""
        from src.utils.alerts import send_alert
        assert callable(send_alert)
    
    def test_alert_accepts_message(self):
        """Test that send_alert accepts a message parameter"""
        from src.utils.alerts import send_alert
        # Should not raise exception
        send_alert("Test message")


class TestWithRetry:
    """Test @with_retry decorator"""
    
    def test_successful_call(self):
        """Test decorator doesn't affect successful calls"""
        from src.utils.alerts import with_retry
        
        @with_retry(max_attempts=3)
        def successful_func():
            return "success"
        
        result = successful_func()
        assert result == "success"
    
    def test_retry_on_failure(self):
        """Test decorator retries on failure"""
        from src.utils.alerts import with_retry
        
        call_count = 0
        
        @with_retry(max_attempts=3, delay_seconds=0.01)
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = failing_func()
        assert result == "success"
        assert call_count == 3
    
    def test_final_failure_raises(self):
        """Test decorator raises after max attempts"""
        from src.utils.alerts import with_retry
        
        @with_retry(max_attempts=3, delay_seconds=0.01, alert_on_final_failure=False)
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fails()


class TestAlertCooldown:
    """Test alert cooldown functionality"""
    
    def test_cooldown_state_exists(self):
        """Test that cooldown state exists"""
        from src.utils.alerts import _last_alert_time, ALERT_COOLDOWN_SECONDS
        
        assert isinstance(_last_alert_time, dict)
        assert ALERT_COOLDOWN_SECONDS == 300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
