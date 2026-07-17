"""
====================================================================
TEST ALERTS MODULE
====================================================================
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSendAlert:
    """Test send_alert function"""
    
    def test_alert_without_config(self):
        """Test alert returns early when not configured"""
        from src.utils.alerts import send_alert
        
        # Mock environment variables
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': '', 'TELEGRAM_CHAT_ID': ''}):
            result = send_alert("Test message", "ERROR")
            assert result is False
    
    def test_alert_with_config_no_requests(self):
        """Test alert works when configured (without actually sending)"""
        from src.utils.alerts import send_alert
        
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': '12345'}):
            with patch('src.utils.alerts.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                result = send_alert("Test message", "ERROR")
                assert result is True
                mock_post.assert_called_once()


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
    
    def test_final_failure_alert(self):
        """Test decorator raises after max attempts"""
        from src.utils.alerts import with_retry
        
        @with_retry(max_attempts=3, delay_seconds=0.01, alert_on_final_failure=False)
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fails()
    
    def test_backoff_delay(self):
        """Test exponential backoff between retries"""
        from src.utils.alerts import with_retry
        import time
        
        call_times = []
        
        @with_retry(max_attempts=3, delay_seconds=0.1, backoff_multiplier=1.0)
        def timed_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("Retry")
            return "done"
        
        timed_func()
        
        # Check delays between calls
        assert len(call_times) == 3
        # Delay should be approximately delay_seconds between calls
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        # Allow some tolerance for test execution time
        assert delay1 >= 0.09  # ~0.1s
        assert delay2 >= 0.09  # ~0.1s


class TestAlertCooldown:
    """Test alert cooldown functionality"""
    
    def test_cooldown_prevents_duplicate_alerts(self):
        """Test that duplicate alerts are rate-limited"""
        from src.utils.alerts import send_alert, _last_alert_time, ALERT_COOLDOWN_SECONDS
        
        # Clear previous state
        _last_alert_time.clear()
        
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': '12345'}):
            with patch('src.utils.alerts.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                # First alert should be sent
                send_alert("Test message 1", "ERROR")
                assert mock_post.call_count == 1
                
                # Second alert with same message should be suppressed
                send_alert("Test message 1", "ERROR")
                assert mock_post.call_count == 1  # Still 1
                
                # Different message should be sent
                send_alert("Test message 2", "ERROR")
                assert mock_post.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
