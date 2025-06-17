"""
Utility functions for the Gunadarma RAG chatbot.

This module contains helper functions for caching, text processing,
and other common operations used throughout the application.
"""

import functools
import hashlib
import time
from typing import Any, Callable, Dict, Optional
import asyncio


class SimpleCache:
    """
    Simple in-memory cache with TTL (Time To Live) support.

    This cache can be used to store expensive operations results
    to improve performance by avoiding redundant API calls.
    """

    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        """
        Initialize the cache.

        Args:
            default_ttl: Default time to live in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if it exists and hasn't expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            return None

        cache_entry = self._cache[key]
        current_time = time.time()

        if current_time > cache_entry["expires_at"]:
            del self._cache[key]
            return None

        return cache_entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl

        expires_at = time.time() + ttl

        self._cache[key] = {"value": value, "expires_at": expires_at}

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            key
            for key, entry in self._cache.items()
            if current_time > entry["expires_at"]
        ]

        for key in expired_keys:
            del self._cache[key]


def create_cache_key(prefix: str, *args: Any) -> str:
    """
    Create a cache key from prefix and arguments.

    Args:
        prefix: Key prefix
        *args: Arguments to include in key

    Returns:
        Generated cache key
    """
    # Combine all arguments into a string
    combined = f"{prefix}:" + ":".join(str(arg) for arg in args)

    # Create hash for consistent key length
    return hashlib.md5(combined.encode()).hexdigest()


def cached_async(ttl: int = 300, cache_instance: Optional[SimpleCache] = None):
    """
    Decorator to cache async function results.

    Args:
        ttl: Time to live in seconds
        cache_instance: Cache instance to use (creates new if None)

    Returns:
        Decorated function
    """
    if cache_instance is None:
        cache_instance = SimpleCache(default_ttl=ttl)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = create_cache_key(func.__name__, *args, *sorted(kwargs.items()))

            # Try to get from cache first
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl)

            return result

        # Add cache management methods to the wrapper
        wrapper.cache_clear = cache_instance.clear
        wrapper.cache_cleanup = cache_instance.cleanup_expired

        return wrapper

    return decorator


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""

    # Remove excessive whitespace
    text = " ".join(text.split())

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0] + "..."

    return text.strip()


def format_response_sources(urls: list) -> str:
    """
    Format source URLs for display in responses.

    Args:
        urls: List of source URLs

    Returns:
        Formatted sources section
    """
    if not urls:
        return ""

    unique_urls = sorted(set(url for url in urls if url))

    if not unique_urls:
        return ""

    sources_section = "\n\n**Sumber:**\n"
    for url in unique_urls:
        sources_section += f"- <{url}>\n"

    return sources_section


async def retry_async(
    func: Callable,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs,
) -> Any:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff_factor: Factor to multiply delay by each retry
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result

    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None
    current_delay = delay

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                break

            await asyncio.sleep(current_delay)
            current_delay *= backoff_factor

    raise last_exception


# Global cache instance for application-wide use
app_cache = SimpleCache(default_ttl=300)
