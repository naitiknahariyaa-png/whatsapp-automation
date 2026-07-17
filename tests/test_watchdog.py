"""
====================================================================
TEST WATCHDOG MODULE
====================================================================
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestWatchdog:
    """Test watchdog functionality"""
    
    @patch('watchdog.requests.get')
    @patch('watchdog.subprocess.run')
    @patch('watchdog.datetime')
    def test_healthy_response(self, mock_datetime, mock_subprocess, mock_get):
        """Test watchdog passes when health check returns 200"""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        mock_datetime.now.return_value = "2024-01-01 12:00:00"
        
        # Import after mocking
        import importlib
        import watchdog
        importlib.reload(watchdog)
        
        # Run check
        watchdog.check_and_recover()
        
        # Should NOT call subprocess restart
        mock_subprocess.assert_not_called()
        mock_get.assert_called_once()
    
    @patch('watchdog.requests.get')
    @patch('watchdog.subprocess.run')
    @patch('watchdog.datetime')
    def test_unhealthy_triggers_restart(self, mock_datetime, mock_subprocess, mock_get):
        """Test watchdog restarts service when health check fails"""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response
        
        mock_datetime.now.return_value = "2024-01-01 12:00:00"
        
        mock_subprocess.run.return_value = MagicMock()
        
        # Import after mocking
        import importlib
        import watchdog
        importlib.reload(watchdog)
        
        # Run check
        watchdog.check_and_recover()
        
        # Should call subprocess restart
        mock_subprocess.assert_called_once()
        assert 'restart' in str(mock_subprocess.call_args)
    
    @patch('watchdog.requests.get')
    @patch('watchdog.subprocess.run')
    @patch('watchdog.datetime')
    def test_connection_error_triggers_restart(self, mock_datetime, mock_subprocess, mock_get):
        """Test watchdog handles connection errors"""
        import requests as req
        
        mock_get.side_effect = req.exceptions.ConnectionError("Connection refused")
        mock_datetime.now.return_value = "2024-01-01 12:00:00"
        mock_subprocess.run.return_value = MagicMock()
        
        # Import after mocking
        import importlib
        import watchdog
        importlib.reload(watchdog)
        
        # Run check
        watchdog.check_and_recover()
        
        # Should call subprocess restart
        mock_subprocess.assert_called_once()
    
    @patch('watchdog.requests.get')
    @patch('watchdog.subprocess.run')
    @patch('watchdog.datetime')
    def test_timeout_error(self, mock_datetime, mock_subprocess, mock_get):
        """Test watchdog handles timeout errors"""
        import requests as req
        
        mock_get.side_effect = req.exceptions.Timeout("Timeout")
        mock_datetime.now.return_value = "2024-01-01 12:00:00"
        mock_subprocess.run.return_value = MagicMock()
        
        # Import after mocking
        import importlib
        import watchdog
        importlib.reload(watchdog)
        
        # Run check
        watchdog.check_and_recover()
        
        # Should call subprocess restart
        mock_subprocess.assert_called_once()


class TestWatchdogConfiguration:
    """Test watchdog configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        import watchdog
        
        assert watchdog.HEALTH_URL == "http://localhost:8000/health"
        assert watchdog.SERVICE_NAME == "whatsapp-bot"
        assert watchdog.TIMEOUT_SECONDS == 10
    
    def test_custom_config(self):
        """Test custom configuration via environment"""
        with patch.dict('os.environ', {
            'HEALTH_CHECK_URL': 'http://custom:9000/health',
            'SYSTEMD_SERVICE_NAME': 'custom-service'
        }):
            import importlib
            import watchdog
            importlib.reload(watchdog)
            
            assert watchdog.HEALTH_URL == "http://custom:9000/health"
            assert watchdog.SERVICE_NAME == "custom-service"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
