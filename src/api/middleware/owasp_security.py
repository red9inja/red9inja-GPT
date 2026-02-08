from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import re

class OWASPSecurityMiddleware:
    """OWASP Top 10 security controls"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive)
        
        # A03:2021 - Injection Prevention
        await self._check_injection(request)
        
        # A05:2021 - Security Misconfiguration
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Security headers
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                headers[b"content-security-policy"] = b"default-src 'self'"
                headers[b"referrer-policy"] = b"strict-origin-when-cross-origin"
                headers[b"permissions-policy"] = b"geolocation=(), microphone=(), camera=()"
                
                message["headers"] = [(k, v) for k, v in headers.items()]
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
    
    async def _check_injection(self, request: Request):
        """Check for SQL injection and XSS patterns"""
        query_params = str(request.query_params)
        
        # SQL injection patterns
        sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bor\b.*=.*)",
            r"(;.*drop\b)",
            r"(--)",
            r"(/\*.*\*/)"
        ]
        
        # XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*="
        ]
        
        for pattern in sql_patterns + xss_patterns:
            if re.search(pattern, query_params, re.IGNORECASE):
                raise HTTPException(status_code=400, detail="Invalid input detected")
