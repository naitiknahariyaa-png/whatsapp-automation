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
        # Need to reimport to get fresh module state
        import importlib
        import src.utils.alerts as alerts_module
        importlib.reload(alerts_module)
        
        # Mock environment variables at module level
        with patch.object(alerts_module, 'TELEGRAM_TOKEN', ''):
            with patch.object(alerts_module, 'TELEGRAM_CHAT_ID', ''):
                # Should just log, not send
                alerts_module.send_alert("Test message", "ERROR")
    
    def test_alert_with_config(self):
        """Test alert works when configured"""
        import importlib
        import src.utils.alerts as alerts_module
        importlib.reload(alerts_module)
        
        with patch.object(alerts_module, 'TELEGRAM_TOKEN', 'test_token'):
            with patch.object(alerts_module, 'TELEGRAM_CHAT_ID', '12345'):
                with patch('requests.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_post.return_value = mock_response
                    
                    # Should not raise exception
                    alerts_module.send_alert("Test message", "ERROR")
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


class TestAlertCooldown:
    """Test alert cooldown functionality"""
    
    def test_cooldown_state(self):
        """Test that cooldown state exists"""
        from src.utils.alerts import _last_alert_time, ALERT_COOLDOWN_SECONDS
        
        # Check cooldown exists
        assert isinstance(_last_alert_time, dict)
        assert ALERT_COOLDOWN_SECONDS == 300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
