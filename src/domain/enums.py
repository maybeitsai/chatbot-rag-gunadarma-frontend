"""Domain enums - Business logic enumerations."""

from enum import Enum


class SearchStrategy(Enum):
    """Search strategy types - simplified to hybrid only."""
    HYBRID = "hybrid"


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
