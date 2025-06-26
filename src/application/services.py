"""Application services - Business logic orchestration."""

import logging
from typing import Dict, Any, Optional, List

from ..core import SearchServiceInterface
from ..domain import SearchQuery, SearchResponse, SearchStrategy, BatchRequest, BatchResponse
from ..infrastructure import RAGApiClient, ApiConfig


logger = logging.getLogger(__name__)


class SearchService(SearchServiceInterface):
    """
    Simplified search service using Hybrid Search only.
    """
    
    def __init__(self, api_config: Optional[ApiConfig] = None):
        """Initialize search service with API client."""
        self.client = RAGApiClient(api_config)

    async def search(self, query: SearchQuery) -> SearchResponse:
        """
        Perform search with hybrid strategy by default.
        """
        # Always use hybrid search
        strategy = SearchStrategy.HYBRID
        logger.info(f"Using search strategy: {strategy.value}")
        
        # Always use hybrid search
        use_hybrid = True
        
        response = await self.client.search(query.text, use_hybrid)
        response.search_type = strategy.value
        
        return response

    async def batch_search(self, batch_request: BatchRequest) -> BatchResponse:
        """
        Perform batch search operations.
        """
        logger.info(f"Processing batch request with {len(batch_request.questions)} questions")
        
        try:
            response = await self.client.batch_search(batch_request)
            logger.info(f"Batch search completed in {response.processing_time:.2f}s")
            return response
        
        except Exception as e:
            logger.error(f"Error in batch search: {e}")
            # Create error response for all questions
            error_results = []
            for question in batch_request.questions:
                from ..domain.value_objects import BatchResult
                error_result = BatchResult(
                    answer=f"Error: {str(e)}",
                    source_urls=[],
                    status="error",
                    source_count=0,
                    response_time=0.0,
                    cached=False,
                    cache_type=None,
                    search_type=None
                )
                error_results.append(error_result)
            
            return BatchResponse(
                results=error_results,
                total_questions=len(batch_request.questions),
                processing_time=0.0
            )

    async def health_check(self) -> Dict[str, Any]:
        """Check service health - always reports hybrid search available."""
        api_healthy = self.client.health_check()
        
        return {
            "service_status": "healthy" if api_healthy else "unhealthy",
            "backend_status": "available" if api_healthy else "unavailable",
            "available_strategies": ["hybrid"]
        }

    async def get_search_suggestions(self, text: str) -> List[str]:
        """Get simple search suggestions."""
        # Return basic suggestions for University Gunadarma
        suggestions = [
            "Bagaimana cara mendaftar kuliah di Universitas Gunadarma?",
            "Program studi apa saja yang tersedia?",
            "Berapa biaya kuliah per semester?",
            "Dimana alamat kampus Universitas Gunadarma?",
            "Fasilitas apa saja yang tersedia di kampus?"
        ]
        return suggestions


class ChatbotService:
    """Service for handling chatbot operations."""
    
    def __init__(self, search_service: SearchServiceInterface):
        self.search_service = search_service
        self.hybrid_available = True
    
    async def process_message(
        self, 
        message: str, 
        strategy: Optional[SearchStrategy] = None,
        search_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process user message and return formatted response."""
        try:
            # Enhanced input validation with detailed logging
            logger.info(f"Processing message: '{message}' (type: {type(message)}, length: {len(message) if message else 0})")
            
            # Validate and sanitize input
            if not message or not isinstance(message, str):
                logger.warning(f"Invalid message type or None: {type(message)}")
                return "❌ **Error:** Pesan tidak valid. Silakan masukkan pertanyaan Anda."
            
            # Strip whitespace and validate again
            message = message.strip()
            if not message:
                logger.warning("Empty message after stripping whitespace")
                return "❌ **Error:** Pesan tidak boleh kosong. Silakan masukkan pertanyaan Anda."
            
            # Validate minimum message length
            if len(message) < 2:
                logger.warning(f"Message too short: '{message}'")
                return "❌ **Error:** Pertanyaan terlalu pendek. Silakan masukkan pertanyaan yang lebih jelas."
            
            # Always use hybrid search
            strategy = SearchStrategy.HYBRID
            
            # Create query with validated message and hybrid strategy
            query = SearchQuery(text=message, strategy=strategy)
            logger.info(f"Created search query successfully for: '{message[:50]}...'")
            
            response = await self.search_service.search(query)
            
            if response.error:
                return f"❌ **Error:** {response.error_message}"
            
            # Always show sources
            formatted_response = self._format_response(response, {'show_sources': True})
            return formatted_response
            
        except ValueError as e:
            # This catches the "Search query text cannot be empty" error
            logger.error(f"ValueError in message processing: {e}")
            return f"❌ **Error:** Terjadi kesalahan validasi: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"❌ **Error:** Terjadi kesalahan saat memproses pertanyaan Anda: {str(e)}"

    async def process_batch_messages(self, batch_request: BatchRequest) -> BatchResponse:
        """Process batch messages and return batch response."""
        try:
            logger.info(f"Processing batch request with {len(batch_request.questions)} questions")
            
            # Validate batch request
            if not batch_request.questions:
                raise ValueError("Batch request must contain at least one question")
            
            # Process through search service
            batch_response = await self.search_service.batch_search(batch_request)
            
            logger.info(f"Batch processing completed in {batch_response.processing_time:.2f}s")
            return batch_response
            
        except Exception as e:
            logger.error(f"Error processing batch messages: {e}")
            # Create error response for all questions
            error_results = []
            for question in batch_request.questions:
                from ..domain.value_objects import BatchResult
                error_result = BatchResult(
                    answer=f"Error: {str(e)}",
                    source_urls=[],
                    status="error",
                    source_count=0,
                    response_time=0.0,
                    cached=False,
                    cache_type=None,
                    search_type=None
                )
                error_results.append(error_result)
            
            return BatchResponse(
                results=error_results,
                total_questions=len(batch_request.questions),
                processing_time=0.0
            )
    
    def _format_response(self, response: SearchResponse, search_options: Optional[Dict[str, Any]] = None) -> str:
        """Format search response for display - always show sources."""
        answer = response.answer
        
        # Apply response formatting rules:
        # Only show sources if the answer is not the standard "not available" message
        standard_message = "Maaf, informasi mengenai hal tersebut tidak tersedia dalam data kami."
        
        # Always add sources if available and it's not the standard "not available" message
        if response.source_urls and answer.strip() != standard_message:
            sources_section = "\n\n**📚 Sumber:**\n"
            for i, url in enumerate(response.source_urls[:3], 1):
                sources_section += f"{i}. {url}\n"
            answer += sources_section
        
        return answer
