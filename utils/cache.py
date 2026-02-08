"""
Redis caching layer
"""

import os
import json
import redis
from typing import Optional, Any
from functools import wraps
import hashlib


class RedisCache:
    """Redis caching for API responses"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        self.default_ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            print(f"Redis set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Redis delete error: {e}")
    
    def clear_user_cache(self, user_id: str):
        """Clear all cache for a user"""
        try:
            pattern = f"user:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Redis clear error: {e}")
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            print(f"Redis increment error: {e}")
            return 0
    
    def expire(self, key: str, ttl: int):
        """Set expiry on key"""
        try:
            self.redis_client.expire(key, ttl)
        except Exception as e:
            print(f"Redis expire error: {e}")


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Generate cache key
            key = f"{key_prefix}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Global cache instance
cache = RedisCache()
