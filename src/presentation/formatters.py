"""Presentation formatters - Response formatting for UI."""

from typing import Dict, Any, List
from ..core import FormatterInterface
from ..domain import SearchResponse


class ResponseFormatter(FormatterInterface):
    """Formatter for search responses and UI elements."""
    
    def __init__(self, show_debug_info: bool = False):
        self.show_debug_info = show_debug_info
    
    def format_search_response(self, response: SearchResponse) -> str:
        """Format search response for display."""
        if response.error:
            return self.format_error(response.error_message)
        
        formatted_text = response.answer
        
        # Add sources if available
        if response.source_urls:
            sources_section = self._format_sources(response.source_urls)
            formatted_text += sources_section
        
        # Add debug info if enabled
        if self.show_debug_info:
            debug_info = self._format_debug_info(response)
            formatted_text += debug_info
        
        return formatted_text
    
    def format_error(self, error: str) -> str:
        """Format error message for display."""
        return f"❌ **Error:** {error}"
    
    def format_suggestions(self, suggestions: List[str]) -> str:
        """Format search suggestions."""
        if not suggestions:
            return "💡 Tidak ada saran yang tersedia saat ini."
        
        formatted_text = "💡 **Saran Pencarian:**\n\n"
        for i, suggestion in enumerate(suggestions, 1):
            formatted_text += f"{i}. {suggestion}\n"
        
        return formatted_text
    
    def format_multi_response(self, responses: Dict[str, SearchResponse]) -> str:
        """Format multiple strategy responses for comparison."""
        formatted_text = "🔍 **Perbandingan Hasil Pencarian:**\n\n"
        
        for strategy, response in responses.items():
            formatted_text += f"**{strategy.title()}:**\n"
            if response.error:
                formatted_text += f"❌ Error: {response.error_message}\n\n"
            else:
                # Show abbreviated answer
                answer = response.answer[:200] + "..." if len(response.answer) > 200 else response.answer
                formatted_text += f"{answer}\n"
                if response.source_count > 0:
                    formatted_text += f"📚 Sumber: {response.source_count} dokumen\n"
                formatted_text += "\n"
        
        return formatted_text
    
    def _format_sources(self, source_urls: List[str]) -> str:
        """Format source URLs for display."""
        sources_section = "\n\n**📚 Sumber:**\n"
        for i, url in enumerate(source_urls[:3], 1):
            sources_section += f"{i}. {url}\n"
        
        if len(source_urls) > 3:
            sources_section += f"... dan {len(source_urls) - 3} sumber lainnya\n"
        
        return sources_section
    
    def _format_debug_info(self, response: SearchResponse) -> str:
        """Format debug information."""
        debug_info = "\n\n**🔧 Debug Info:**\n"
        debug_info += f"- Response Time: {response.response_time:.2f}s\n"
        debug_info += f"- Search Type: {response.search_type}\n"
        debug_info += f"- Cached: {'Yes' if response.cached else 'No'}\n"
        debug_info += f"- Source Count: {response.source_count}\n"
        
        return debug_info


def format_response_sources(source_urls: List[str]) -> str:
    """Utility function to format response sources."""
    formatter = ResponseFormatter()
    return formatter._format_sources(source_urls)
