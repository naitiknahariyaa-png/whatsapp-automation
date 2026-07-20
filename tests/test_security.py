"""
🧪 Security Tests
================
Test security module functionality.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.security.validator import InputValidator, ValidationLevel, ValidationResult
    from src.security.sanitizer import Sanitizer
    from src.security.config import SecurityConfig
except ImportError:
    pytest.skip("Security module not available", allow_module_level=True)


class TestInputValidator:
    """Test cases for InputValidator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator(level=ValidationLevel.MODERATE)
    
    # Phone validation tests
    def test_valid_indian_phone(self):
        """Test valid Indian phone numbers."""
        result = self.validator.validate_phone("+919876543210")
        assert result.valid is True
        assert result.sanitized_value == "+919876543210"
    
    def test_valid_phone_with_dashes(self):
        """Test phone with dashes gets sanitized."""
        result = self.validator.validate_phone("+91-98765-43210")
        assert result.valid is True
        assert result.sanitized_value == "+919876543210"
    
    def test_invalid_phone_too_short(self):
        """Test phone that's too short."""
        result = self.validator.validate_phone("+9198765")
        assert result.valid is False
    
    def test_invalid_phone_letters(self):
        """Test phone with letters."""
        result = self.validator.validate_phone("+91ABCDEF")
        assert result.valid is False
    
    def test_empty_phone(self):
        """Test empty phone number."""
        result = self.validator.validate_phone("")
        assert result.valid is False
    
    # Text validation tests
    def test_valid_text(self):
        """Test valid text."""
        result = self.validator.validate_text("Hello, World!")
        assert result.valid is True
    
    def test_text_with_script_tag(self):
        """Test text with script tag (moderated - gets removed)."""
        result = self.validator.validate_text("Hello <script>alert('xss')</script>")
        # In moderate mode, dangerous content is removed
        assert result.valid is True
    
    def test_text_too_long_strict(self):
        """Test text too long in strict mode."""
        strict_validator = InputValidator(level=ValidationLevel.STRICT)
        long_text = "x" * 2000
        result = strict_validator.validate_text(long_text, max_length=1000)
        assert result.valid is False
    
    def test_empty_text(self):
        """Test empty text."""
        result = self.validator.validate_text("")
        assert result.valid is False
    
    # API key validation tests
    def test_valid_api_key(self):
        """Test valid API key format."""
        result = self.validator.validate_api_key("sk_test_12345678901234567890")
        assert result.valid is True
    
    def test_invalid_api_key_too_short(self):
        """Test API key too short."""
        result = self.validator.validate_api_key("short")
        assert result.valid is False
    
    # SQL injection detection
    def test_sql_injection_detected(self):
        """Test SQL injection pattern detection."""
        assert self.validator.check_sql_injection("SELECT * FROM users") is True
        assert self.validator.check_sql_injection("'; DROP TABLE users;--") is True
        assert self.validator.check_sql_injection("Hello, World!") is False


class TestSanitizer:
    """Test cases for Sanitizer."""
    
    def test_sanitize_message_removes_html(self):
        """Test HTML tags are removed."""
        result = Sanitizer.sanitize_message("Hello <b>World</b>")
        assert "<b>" not in result
        assert "World" in result
    
    def test_sanitize_message_removes_script(self):
        """Test script tags are removed."""
        result = Sanitizer.sanitize_message("Hello <script>alert('xss')</script>")
        assert "<script" not in result.lower()
    
    def test_sanitize_message_removes_dangerous_strings(self):
        """Test dangerous strings are removed."""
        result = Sanitizer.sanitize_message("Click javascript:alert('xss')")
        assert "javascript:" not in result.lower()
    
    def test_sanitize_phone(self):
        """Test phone sanitization."""
        result = Sanitizer.sanitize_phone("+91-98765-43210")
        assert result == "+919876543210"
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        result = Sanitizer.sanitize_filename("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
    
    def test_remove_pii(self):
        """Test PII removal."""
        result = Sanitizer.remove_pii("Email me at test@example.com")
        assert "[EMAIL]" in result
        assert "test@example.com" not in result


class TestSecurityConfig:
    """Test cases for SecurityConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = SecurityConfig()
        assert config.rate_limit_enabled is True
        assert config.rate_limit_per_minute == 60
    
    def test_config_from_env(self):
        """Test configuration from environment."""
        config = SecurityConfig.from_env()
        assert isinstance(config.rate_limit_per_minute, int)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
