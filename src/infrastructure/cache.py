"""Infrastructure cache implementations."""

import asyncio
import time
from typing import Any, Optional, Dict
from ..core import CacheInterface


class SimpleCache(CacheInterface):
    """Simple in-memory cache implementation."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
            
        item = self._cache[key]
        if time.time() > item['expires']:
            await self.delete(key)
            return None
            
        return item['value']
    
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache."""
        if ttl is None:
            ttl = self._default_ttl
            
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()


# Global cache instance
app_cache = SimpleCache()


def cached_async(ttl: int = 300):
    """Decorator for caching async function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get from cache
            cached_result = await app_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await app_cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
