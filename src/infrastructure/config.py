"""Infrastructure configuration implementations."""

import os
from dataclasses import dataclass
from ..core import ConfigInterface


@dataclass
class ApiConfig:
    """Configuration for API client."""
    base_url: str
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    default_search_preset: str = "balanced"

    @classmethod
    def from_env(cls) -> 'ApiConfig':
        """Create ApiConfig from environment variables."""
        base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        return cls(base_url=base_url)


@dataclass
class SearchConfig:
    """Configuration for search operations."""
    max_results: int = 10
    cache_ttl: int = 300
    enable_caching: bool = True
    default_strategy: str = "hybrid"

    @classmethod
    def from_env(cls) -> 'SearchConfig':
        """Create SearchConfig from environment variables."""
        return cls(
            max_results=int(os.getenv("SEARCH_MAX_RESULTS", "10")),
            cache_ttl=int(os.getenv("CACHE_TTL", "300")),
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            default_strategy=os.getenv("DEFAULT_SEARCH_STRATEGY", "hybrid")
        )
