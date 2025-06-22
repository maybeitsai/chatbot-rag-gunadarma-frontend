"""Presentation controllers - Handle UI interactions."""

import logging
from typing import Optional, Dict, Any

from ..application import ChatUseCase, HealthCheckUseCase, SearchUseCase
from ..domain import SearchStrategy
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
    
    async def process_message(self, message_content: str) -> str:
        """Process user message and return response."""
        try:
            # Check for special commands
            if message_content.startswith("/"):
                return await self.handle_special_commands(message_content)
            
            # Process regular message
            response_text = await self.chat_use_case.process_user_message(message_content)
            return response_text
            
        except Exception as e:
            logger.error(f"Error in message handling: {e}")
            return f"❌ **Error:** Terjadi kesalahan yang tidak terduga: {str(e)}"
    
    async def handle_special_commands(self, command: str) -> str:
        """Handle special commands for advanced features."""
        if not self.hybrid_available:
            return "❌ Perintah khusus memerlukan hybrid search yang tidak tersedia."
        
        command = command.lower()
        
        if command.startswith("/help"):
            return self._get_help_text()
        elif command.startswith("/suggest "):
            query = command[9:].strip()
            if query:
                return "💡 **Saran:** Fitur ini akan segera tersedia."
            else:
                return "❌ Gunakan format: `/suggest [pertanyaan anda]`"
        elif command.startswith("/compare "):
            query = command[9:].strip()
            if query:
                return "🔍 **Info:** Fitur perbandingan akan segera tersedia."
            else:
                return "❌ Gunakan format: `/compare [pertanyaan anda]`"
        elif command.startswith("/health"):
            return await self._get_health_status()
        else:
            return "❌ Perintah tidak dikenali. Ketik `/help` untuk melihat perintah yang tersedia."
    
    def _get_help_text(self) -> str:
        """Get help text."""
        return """
**🔧 Perintah Khusus:**

- `/help` - Tampilkan bantuan ini
- `/suggest [pertanyaan]` - Dapatkan saran pencarian untuk pertanyaan
- `/compare [pertanyaan]` - Bandingkan hasil dari berbagai strategi pencarian
- `/health` - Cek status sistem

**💡 Tips:**
- Gunakan pertanyaan yang spesifik untuk hasil yang lebih baik
- Sistem akan otomatis memilih strategi pencarian terbaik
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

**Strategi Tersedia:** {', '.join(health_info.get('available_strategies', []))}
            """
        except Exception as e:
            return f"❌ Error checking health: {str(e)}"
