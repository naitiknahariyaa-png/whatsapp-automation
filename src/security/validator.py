"""
🔒 Input Validation Module
=========================
Validates and sanitizes all user inputs to prevent injection attacks,
XSS, and other security vulnerabilities.
"""

import re
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


class ValidationError(Exception):
    """Custom validation error"""
    pass


class ValidationLevel(Enum):
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


@dataclass
class ValidationResult:
    """Result of validation"""
    valid: bool
    error: Optional[str] = None
    sanitized_value: Optional[str] = None


class InputValidator:
    """
    Validates user inputs for WhatsApp automation.
    
    Usage:
        validator = InputValidator()
        result = validator.validate_phone("+91-9876543210")
        if result.valid:
            print(f"Valid phone: {result.sanitized_value}")
        else:
            print(f"Error: {result.error}")
    """
    
    # Phone number patterns for various countries
    PHONE_PATTERNS = {
        'india': r'^\+?91[6-9]\d{9}$',
        'us': r'^\+?1?\d{10}$',
        'generic': r'^\+?\d{10,15}$'
    }
    
    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',  # JS injection
        r'on\w+\s*=',  # Event handlers
        r'<!--',  # HTML comments
        r'-->',
        r'<iframe',
        r'<object',
        r'<embed',
        r'\$\{',  # Template injection
        r'\{\{',  # Template injection
        r'\}\}',
    ]
    
    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        r"(--|;|/\*|\*/|@|@@)",
        r"OR\s+1\s*=\s*1",
        r"AND\s+1\s*=\s*1",
    ]
    
    def __init__(self, level: ValidationLevel = ValidationLevel.MODERATE):
        self.level = level
        
    def validate_phone(self, phone: str) -> ValidationResult:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number string
            
        Returns:
            ValidationResult with sanitized value
        """
        if not phone:
            return ValidationResult(False, "Phone number is required")
        
        # Remove whitespace and dashes
        sanitized = re.sub(r'[\s\-]+', '', phone)
        
        # Check against India pattern (most common for this app)
        if re.match(self.PHONE_PATTERNS['india'], sanitized):
            return ValidationResult(True, sanitized_value=sanitized)
        
        # Check against generic pattern
        if re.match(self.PHONE_PATTERNS['generic'], sanitized):
            return ValidationResult(True, sanitized_value=sanitized)
        
        return ValidationResult(False, "Invalid phone number format")
    
    def validate_text(self, text: str, max_length: int = 1000) -> ValidationResult:
        """
        Validate text input.
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            
        Returns:
            ValidationResult with sanitized value
        """
        if not text:
            return ValidationResult(False, "Text is required")
        
        if len(text) > max_length:
            if self.level == ValidationLevel.STRICT:
                return ValidationResult(False, f"Text exceeds max length ({max_length})")
            text = text[:max_length]
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                if self.level == ValidationLevel.STRICT:
                    return ValidationResult(False, "Text contains dangerous content")
                # Remove dangerous content
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return ValidationResult(True, sanitized_value=text.strip())
    
    def validate_api_key(self, key: str) -> ValidationResult:
        """
        Validate API key format.
        
        Args:
            key: API key string
            
        Returns:
            ValidationResult
        """
        if not key:
            return ValidationResult(False, "API key is required")
        
        # Basic format check (alphanumeric, dashes, underscores)
        if not re.match(r'^[a-zA-Z0-9_\-]{20,}$', key):
            return ValidationResult(False, "Invalid API key format")
        
        return ValidationResult(True, sanitized_value=key)
    
    def validate_url(self, url: str) -> ValidationResult:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            ValidationResult
        """
        if not url:
            return ValidationResult(False, "URL is required")
        
        # Basic URL pattern
        url_pattern = r'^https?://[\w\-\.]+(:\d+)?(/[\w\-\./?%&=]*)?$'
        
        if not re.match(url_pattern, url):
            return ValidationResult(False, "Invalid URL format")
        
        # Check for localhost in strict mode
        if self.level == ValidationLevel.STRICT:
            localhost_patterns = ['localhost', '127.0.0.1', '0.0.0.0']
            if any(pattern in url.lower() for pattern in localhost_patterns):
                return ValidationResult(False, "Localhost URLs not allowed in production")
        
        return ValidationResult(True, sanitized_value=url.rstrip('/'))
    
    def validate_customer_data(self, data: dict) -> tuple[bool, Optional[str], dict]:
        """
        Validate complete customer data.
        
        Args:
            data: Customer data dictionary
            
        Returns:
            Tuple of (is_valid, error_message, sanitized_data)
        """
        sanitized = {}
        
        # Validate name
        if 'name' in data:
            name_result = self.validate_text(data['name'], max_length=100)
            if not name_result.valid:
                return False, f"Invalid name: {name_result.error}", {}
            sanitized['name'] = name_result.sanitized_value
        
        # Validate phone
        if 'phone' in data:
            phone_result = self.validate_phone(data['phone'])
            if not phone_result.valid:
                return False, f"Invalid phone: {phone_result.error}", {}
            sanitized['phone'] = phone_result.sanitized_value
        
        # Validate address (if present)
        if 'address' in data:
            addr_result = self.validate_text(data['address'], max_length=500)
            if not addr_result.valid:
                return False, f"Invalid address: {addr_result.error}", {}
            sanitized['address'] = addr_result.sanitized_value
        
        return True, None, sanitized
    
    def check_sql_injection(self, text: str) -> bool:
        """
        Check if text contains SQL injection patterns.
        
        Args:
            text: Text to check
            
        Returns:
            True if SQL injection detected
        """
        for pattern in self.SQL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


# Singleton instance
validator = InputValidator()
