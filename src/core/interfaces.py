"""Core interfaces - Abstract base classes and protocols."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from ..domain import SearchQuery, SearchResponse, StarterQuestion


class SearchServiceInterface(ABC):
    """Interface for search services."""
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform a search operation."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        pass
    
    @abstractmethod
    async def get_search_suggestions(self, text: str) -> List[str]:
        """Get search suggestions."""
        pass


class ApiClientInterface(ABC):
    """Interface for API clients."""
    
    @abstractmethod
    async def search(self, query: str) -> SearchResponse:
        """Perform search via API."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check API health."""
        pass


class CacheInterface(ABC):
    """Interface for caching implementations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass


class ConfigInterface(Protocol):
    """Interface for configuration objects."""
    
    @classmethod
    def from_env(cls) -> 'ConfigInterface':
        """Create config from environment variables."""
        ...


class FormatterInterface(ABC):
    """Interface for response formatters."""
    
    @abstractmethod
    def format_search_response(self, response: SearchResponse) -> str:
        """Format search response for display."""
        pass
    
    @abstractmethod
    def format_error(self, error: str) -> str:
        """Format error message for display."""
        pass
