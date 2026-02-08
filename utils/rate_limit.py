"""
Rate limiting middleware
"""

import os
import time
from fastapi import HTTPException, Request
from utils.cache import cache


class RateLimiter:
    """Rate limiting using Redis"""
    
    def __init__(self):
        self.rate_limit = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
        self.window = 60  # seconds
    
    def check_rate_limit(self, user_id: str, endpoint: str = "general"):
        """Check if user has exceeded rate limit"""
        key = f"rate_limit:{user_id}:{endpoint}"
        
        # Get current count
        count = cache.redis_client.get(key)
        
        if count is None:
            # First request in window
            cache.redis_client.setex(key, self.window, 1)
            return True
        
        count = int(count)
        
        if count >= self.rate_limit:
            # Rate limit exceeded
            ttl = cache.redis_client.ttl(key)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds."
            )
        
        # Increment counter
        cache.redis_client.incr(key)
        return True
    
    def get_remaining(self, user_id: str, endpoint: str = "general") -> int:
        """Get remaining requests in current window"""
        key = f"rate_limit:{user_id}:{endpoint}"
        count = cache.redis_client.get(key)
        
        if count is None:
            return self.rate_limit
        
        return max(0, self.rate_limit - int(count))


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Skip rate limiting for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    # Get user from token (if authenticated)
    user_id = getattr(request.state, "user_id", request.client.host)
    
    # Check rate limit
    try:
        rate_limiter.check_rate_limit(user_id)
    except HTTPException as e:
        return e
    
    # Add rate limit headers
    response = await call_next(request)
    remaining = rate_limiter.get_remaining(user_id)
    
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.rate_limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response
