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
        # Robust validation for text input
        if not self.text or not isinstance(self.text, str) or not self.text.strip():
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


@dataclass(frozen=True)
class BatchRequest:
    """Value object representing a batch request."""
    questions: List[str]
    use_cache: bool = True
    use_hybrid: bool = True
    
    def __post_init__(self):
        if not self.questions or not isinstance(self.questions, list):
            raise ValueError("Questions list cannot be empty")
        if not all(isinstance(q, str) and q.strip() for q in self.questions):
            raise ValueError("All questions must be non-empty strings")


@dataclass(frozen=True)
class BatchResult:
    """Value object representing a single result in batch response."""
    answer: str
    source_urls: List[str]
    status: str
    source_count: int
    response_time: float
    cached: bool
    cache_type: Optional[str]
    search_type: Optional[str]


@dataclass(frozen=True)
class BatchResponse:
    """Value object representing a batch response."""
    results: List[BatchResult]
    total_questions: int
    processing_time: float
