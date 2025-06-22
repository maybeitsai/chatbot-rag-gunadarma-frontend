"""Domain value objects - Immutable value containers."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .enums import SearchStrategy, ResponseStatus


@dataclass(frozen=True)
class SearchQuery:
    """Value object representing a search query."""
    text: str
    strategy: Optional[SearchStrategy] = None
    max_results: int = 10
    
    def __post_init__(self):
        if not self.text.strip():
            raise ValueError("Search query text cannot be empty")


@dataclass(frozen=True)
class SearchResult:
    """Value object representing a single search result."""
    content: str
    source_url: str
    title: str
    relevance_score: float
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class StarterQuestion:
    """Value object for starter questions."""
    content: str
    icon: str
    category: str
