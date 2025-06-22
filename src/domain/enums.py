"""Domain enums - Business logic enumerations."""

from enum import Enum


class SearchStrategy(Enum):
    """Search strategy types."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    SMART = "smart"
    ACADEMIC = "academic"
    ADMINISTRATIVE = "administrative"
    FACILITY = "facility"
    QUICK = "quick"


class SearchType(Enum):
    """Search types for different use cases."""
    COMPREHENSIVE = "comprehensive"
    FOCUSED = "focused"
    QUICK = "quick"


class MessageType(Enum):
    """Message types for chat interface."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ResponseStatus(Enum):
    """Response status types."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
