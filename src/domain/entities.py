"""Domain entities - Business entities with identity."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .value_objects import SearchResult, SearchQuery
from .enums import ResponseStatus, SearchStrategy


@dataclass
class SearchResponse:
    """Entity representing a complete search response."""
    query: SearchQuery
    answer: str
    results: List[SearchResult] = field(default_factory=list)
    status: ResponseStatus = ResponseStatus.SUCCESS
    error_message: Optional[str] = None
    source_urls: List[str] = field(default_factory=list)
    response_time: float = 0.0
    cached: bool = False
    cache_type: Optional[str] = None
    search_type: Optional[str] = None
    source_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def error(self) -> bool:
        """Check if response has error."""
        return self.status == ResponseStatus.ERROR
    
    def add_result(self, result: SearchResult):
        """Add a search result."""
        self.results.append(result)
        if result.source_url not in self.source_urls:
            self.source_urls.append(result.source_url)
        self.source_count = len(self.source_urls)


@dataclass
class ChatProfile:
    """Entity representing a chat profile configuration."""
    name: str
    description: str
    icon: str
    starters: List[SearchQuery] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_starter(self, query: SearchQuery):
        """Add a starter question."""
        self.starters.append(query)
