"""Presentation controllers - Handle UI interactions."""

import logging
from typing import Optional, Dict, Any

from ..application import ChatUseCase, HealthCheckUseCase, SearchUseCase, BatchSearchUseCase
from ..domain import SearchStrategy, BatchRequest, BatchResponse
from .formatters import ResponseFormatter


logger = logging.getLogger(__name__)


class ChatController:
    """Controller for chat interactions."""
    
    def __init__(
        self, 
        chat_use_case: ChatUseCase,
        search_use_case: SearchUseCase,
        health_check_use_case: HealthCheckUseCase,
        formatter: ResponseFormatter
    ):
        self.chat_use_case = chat_use_case
        self.search_use_case = search_use_case
        self.health_check_use_case = health_check_use_case
        self.formatter = formatter
        self.hybrid_available = True
    
    async def process_message(
        self, 
        message_content: str,
        search_strategy: str = None,
        show_sources: bool = True
    ) -> str:
        """Process user message and return response."""
        try:
            if message_content.startswith("/"):
                return await self.handle_special_commands(message_content)
            
            # Always use hybrid search - no fallback
            search_options = {                
                'strategy': SearchStrategy.HYBRID.value,
                'show_sources': True
            }
            
            response_text = await self.chat_use_case.process_user_message(
                message_content, 
                search_options=search_options
            )
            return response_text
            
        except Exception as e:
            logger.error(f"Error in message handling: {e}")
            return f"❌ **Error:** Terjadi kesalahan yang tidak terduga: {str(e)}"
    
    async def handle_special_commands(self, command: str) -> str:
        """Handle special commands for advanced features."""
        command = command.lower()
        
        if command.startswith("/help"):
            return self._get_help_text()
        elif command.startswith("/health"):
            return await self._get_health_status()
        else:
            return "❌ Perintah tidak dikenali. Ketik `/help` untuk melihat perintah yang tersedia."
    
    def _get_help_text(self) -> str:
        """Get help text."""
        return """
**🔧 Perintah Khusus:**

- `/help` - Tampilkan bantuan ini
- `/health` - Cek status sistem

**💡 Tips:**
- Gunakan pertanyaan yang spesifik untuk hasil yang lebih baik
- Sistem menggunakan Hybrid Search dengan sumber otomatis
        """
    
    async def _get_health_status(self) -> str:
        """Get health status."""
        try:
            health_info = await self.health_check_use_case.execute()
            return f"""
**🏥 Status Sistem:**

**Service:** {health_info.get('service_status', 'Unknown')}
**Backend:** {health_info.get('backend_status', 'Unknown')}
**Mode:** Hybrid Search ✅

**Strategi Tersedia:** Hybrid Search
            """
        except Exception as e:
            return f"❌ Error checking health: {str(e)}"


class BatchController:
    """Controller for batch operations."""
    
    def __init__(
        self,
        chat_use_case: ChatUseCase,
        batch_search_use_case: BatchSearchUseCase,
        formatter: ResponseFormatter
    ):
        self.chat_use_case = chat_use_case
        self.batch_search_use_case = batch_search_use_case
        self.formatter = formatter
    
    async def process_batch_request(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process batch request and return JSON response."""
        try:
            # Validate input
            if not batch_data.get("questions"):
                raise ValueError("Questions list is required")
            
            if not isinstance(batch_data["questions"], list):
                raise ValueError("Questions must be a list")
            
            if not all(isinstance(q, str) and q.strip() for q in batch_data["questions"]):
                raise ValueError("All questions must be non-empty strings")
            
            # Create batch request
            batch_request = BatchRequest(
                questions=batch_data["questions"],
                use_cache=batch_data.get("use_cache", True),
                use_hybrid=batch_data.get("use_hybrid", True)
            )
            
            # Process through use case
            batch_response = await self.chat_use_case.process_batch_messages(batch_request)
            
            # Convert to API response format
            api_response = {
                "results": [
                    {
                        "answer": result.answer,
                        "source_urls": result.source_urls,
                        "status": result.status,
                        "source_count": result.source_count,
                        "response_time": result.response_time,
                        "cached": result.cached,
                        "cache_type": result.cache_type,
                        "search_type": result.search_type
                    }
                    for result in batch_response.results
                ],
                "total_questions": batch_response.total_questions,
                "processing_time": batch_response.processing_time
            }
            
            logger.info(f"Batch request processed successfully: {batch_response.total_questions} questions in {batch_response.processing_time:.2f}s")
            return api_response
            
        except ValueError as e:
            logger.error(f"Validation error in batch request: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
        except Exception as e:
            logger.error(f"Error processing batch request: {e}")
            return {
                "error": f"Internal server error: {str(e)}",
                "status": "error"
            }
