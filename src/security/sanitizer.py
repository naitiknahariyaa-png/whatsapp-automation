"""
🧹 Input Sanitization Module
===========================
Sanitizes user inputs to prevent XSS, injection, and other attacks.
"""

import html
import re
from typing import Any, Dict


class Sanitizer:
    """
    Sanitizes data for safe storage and display.
    
    Usage:
        sanitizer = Sanitizer()
        clean = sanitizer.sanitize_message("Hello <script>alert('xss')</script>")
        # Returns: "Hello alert('xss')"
    """
    
    # HTML tags to allow (safe subset)
    ALLOWED_TAGS = {'b', 'i', 'u', 'em', 'strong', 'br', 'p'}
    
    # Dangerous strings
    DANGEROUS_STRINGS = [
        '<script',
        'javascript:',
        'onerror=',
        'onclick=',
        'onload=',
        'onmouseover=',
        '<iframe',
        '<object',
        '<embed',
        'data:',
        'vbscript:',
    ]
    
    @classmethod
    def sanitize_message(cls, message: str) -> str:
        """
        Sanitize a message for safe display.
        
        Args:
            message: Raw message text
            
        Returns:
            Sanitized message
        """
        if not message:
            return ""
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', message)
        
        # Escape HTML entities
        clean = html.escape(clean)
        
        # Remove dangerous strings
        for dangerous in cls.DANGEROUS_STRINGS:
            clean = clean.replace(dangerous.lower(), '')
        
        # Remove excess whitespace
        clean = re.sub(r'\s+', ' ', clean)
        
        return clean.strip()
    
    @classmethod
    def sanitize_phone(cls, phone: str) -> str:
        """
        Sanitize phone number - keep only digits and +.
        
        Args:
            phone: Raw phone number
            
        Returns:
            Clean phone number
        """
        if not phone:
            return ""
        
        # Keep only digits and plus
        clean = re.sub(r'[^\d+]', '', phone)
        
        return clean
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal.
        
        Args:
            filename: Raw filename
            
        Returns:
            Safe filename
        """
        if not filename:
            return "unnamed"
        
        # Remove path separators
        clean = filename.replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        clean = re.sub(r'[^\w\-_.]', '_', clean)
        
        # Limit length
        if len(clean) > 255:
            name, ext = clean.rsplit('.', 1) if '.' in clean else (clean, '')
            name = name[:255 - len(ext) - 1]
            clean = f"{name}.{ext}" if ext else name
        
        return clean
    
    @classmethod
    def sanitize_json(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary values.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_message(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_json(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_message(v) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @classmethod
    def remove_pii(cls, message: str) -> str:
        """
        Remove potential PII from message (optional feature).
        
        Args:
            message: Raw message
            
        Returns:
            Message with potential PII redacted
        """
        # Redact email addresses
        message = re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', '[EMAIL]', message)
        
        # Redact phone numbers (various formats)
        message = re.sub(r'\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', '[PHONE]', message)
        
        # Redact credit card numbers (basic pattern)
        message = re.sub(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', '[CARD]', message)
        
        # Redact Aadhaar-like numbers (12 digits)
        message = re.sub(r'\b\d{12}\b', '[ID]', message)
        
        return message


# Singleton instance
sanitizer = Sanitizer()
