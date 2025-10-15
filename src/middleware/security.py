"""
Security middleware for adding security headers
"""
from flask import make_response


def add_security_headers(response):
    """
    Add security headers to all responses
    
    Args:
        response: Flask response object
        
    Returns:
        Flask response object with security headers
    """
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Strict Transport Security (HTTPS only)
    # Only enable in production with HTTPS
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' http://localhost:* https:;"
    )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy (formerly Feature Policy)
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=()"
    )
    
    return response


def register_security_middleware(app):
    """
    Register security middleware with Flask app
    
    Args:
        app: Flask application instance
    """
    @app.after_request
    def apply_security_headers(response):
        """Apply security headers to all responses"""
        return add_security_headers(response)
    
    app.logger.info("✅ Security headers middleware registered")

