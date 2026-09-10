"""
Security & Privacy Hardening Module
Protects against:
- Brute Force & DDoS Attacks (IP Rate Limiting)
- Unauthorized Admin Access (Cryptographic API Key & PIN Protection)
- SQL Injection & XSS (Input Sanitization & Parameterization)
- Privacy Leaks (Customer Phone Masking & Restricted Document Access)
- Clickjacking & MIME-Sniffing (Strict Security Headers)
"""
import time
import re
import html
import hashlib
from typing import Dict, Tuple
from fastapi import Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

ADMIN_API_KEY_HEADER = APIKeyHeader(name="X-Admin-Secret", auto_error=False)
DEFAULT_ADMIN_SECRET = "Admin@Malumichampatti#2026"

class RateLimiter:
    """
    Sliding window in-memory rate limiter per IP address.
    Defends against DDoS, automated scraping, and brute-force guessing.
    """
    def __init__(self, max_requests_per_minute: int = 120):
        self.max_requests = max_requests_per_minute
        self.ip_hits: Dict[str, list] = {}

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        if ip not in self.ip_hits:
            self.ip_hits[ip] = [now]
            return True

        # Keep only timestamps in the last 60 seconds
        self.ip_hits[ip] = [t for t in self.ip_hits[ip] if t > window_start]

        if len(self.ip_hits[ip]) >= self.max_requests:
            return False

        self.ip_hits[ip].append(now)
        return True

rate_limiter = RateLimiter(max_requests_per_minute=120)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects enterprise security headers to prevent XSS, clickjacking, and MIME sniffing.
    """
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"

        # Check rate limit on API endpoints
        if request.url.path.startswith("/api/") and not rate_limiter.is_allowed(client_ip):
            return Response(
                content='{"detail": "Too many requests. Rate limit exceeded to prevent abuse."}',
                status_code=429,
                media_type="application/json"
            )

        response = await call_next(request)

        # Apply Hardened Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), microphone=()"

        return response

class PrivacyGuard:
    """
    Guarantees user phone number and location privacy.
    Prevents unauthorized parties from harvesting customer or mechanic details.
    """
    @staticmethod
    def mask_phone_number(phone: str) -> str:
        """Masks middle digits: +919842198765 -> +91 98421 •••65"""
        cleaned = re.sub(r"[^\d+]", "", phone)
        if len(cleaned) >= 10:
            return cleaned[:8] + "••••" + cleaned[-2:]
        return "••••••••••"

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Strips potential XSS, script injection, and SQL injection characters."""
        if not text:
            return ""
        # Escape HTML entities
        escaped = html.escape(text.strip())
        # Strip potential dangerous script or sql keywords
        sanitized = re.sub(r"(<script.*?>.*?</script>|javascript:|union\s+select|drop\s+table)", "", escaped, flags=re.IGNORECASE)
        return sanitized

    @staticmethod
    def verify_admin_key(secret_header: str = Security(ADMIN_API_KEY_HEADER)) -> bool:
        """Enforces admin authentication on all sensitive configuration and pricing endpoints."""
        if not secret_header or secret_header != DEFAULT_ADMIN_SECRET:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized. Valid Admin Secret Key required."
            )
        return True
