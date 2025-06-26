"""Application use cases - Specific business operations."""

from typing import Dict, Any, Optional, List
from ..domain import SearchQuery, SearchResponse, SearchStrategy, BatchRequest, BatchResponse
from ..core import SearchServiceInterface
from .services import ChatbotService


class SearchUseCase:
    """Use case for search operations."""
    
    def __init__(self, search_service: SearchServiceInterface):
        self.search_service = search_service
    
    async def execute(self, query: str, strategy: Optional[SearchStrategy] = None) -> SearchResponse:
        """Execute search use case."""
        search_query = SearchQuery(text=query, strategy=strategy)
        return await self.search_service.search(search_query)


class BatchSearchUseCase:
    """Use case for batch search operations."""
    
    def __init__(self, search_service: SearchServiceInterface):
        self.search_service = search_service
    
    async def execute(self, batch_request: BatchRequest) -> BatchResponse:
        """Execute batch search use case."""
        return await self.search_service.batch_search(batch_request)


class ChatUseCase:
    """Use case for chat operations."""
    
    def __init__(self, chatbot_service: ChatbotService):
        self.chatbot_service = chatbot_service
    
    async def process_user_message(
        self, 
        message: str, 
        strategy: Optional[SearchStrategy] = None,
        search_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process user message through chatbot service."""
        return await self.chatbot_service.process_message(message, strategy, search_options)

    async def process_batch_messages(self, batch_request: BatchRequest) -> BatchResponse:
        """Process batch messages through chatbot service."""
        return await self.chatbot_service.process_batch_messages(batch_request)


class HealthCheckUseCase:
    """Use case for health check operations."""
    
    def __init__(self, search_service: SearchServiceInterface):
        self.search_service = search_service
    
    async def execute(self) -> Dict[str, Any]:
        """Execute health check use case."""
        return await self.search_service.health_check()
