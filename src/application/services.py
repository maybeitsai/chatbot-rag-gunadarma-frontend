"""Application services - Business logic orchestration."""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from ..core import SearchServiceInterface
from ..domain import SearchQuery, SearchResponse, SearchStrategy
from ..infrastructure import RAGApiClient, ApiConfig


logger = logging.getLogger(__name__)


class SearchService(SearchServiceInterface):
    """
    High-level search service with intelligent search strategy selection.
    
    This service provides different search strategies optimized for various
    types of queries and use cases.
    """
    
    def __init__(self, api_config: Optional[ApiConfig] = None):
        """Initialize search service with API client."""
        self.client = RAGApiClient(api_config)
        
        # Keywords for strategy detection
        self._strategy_keywords = {
            SearchStrategy.ACADEMIC: [
                "mata kuliah", "sks", "kurikulum", "silabus", "dosen", 
                "jurusan", "fakultas", "semester", "ujian", "nilai",
                "skripsi", "thesis", "akademik", "pendidikan"
            ],
            SearchStrategy.ADMINISTRATIVE: [
                "pendaftaran", "administrasi", "pembayaran", "spp", "uang kuliah",
                "dokumen", "berkas", "persyaratan", "prosedur", "formulir",
                "registrasi", "kartu mahasiswa", "transkrip"
            ],
            SearchStrategy.FACILITY: [
                "gedung", "ruang", "laboratorium", "perpustakaan", "kantin",
                "parkir", "fasilitas", "lokasi", "alamat", "kampus",
                "lab", "auditorium", "aula"
            ]
        }

    async def search(self, query: SearchQuery) -> SearchResponse:
        """
        Perform intelligent search with automatic or specified strategy.
        """
        # Auto-detect strategy if not provided
        strategy = query.strategy
        if strategy is None:
            strategy = self._detect_search_strategy(query.text)
            
        logger.info(f"Using search strategy: {strategy.value}")
        
        # Perform search via API client
        response = await self.client.search(query.text)
        
        # Add strategy info to response
        response.search_type = strategy.value
        
        return response

    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        api_healthy = self.client.health_check()
        
        return {
            "service_status": "healthy" if api_healthy else "unhealthy",
            "backend_status": "available" if api_healthy else "unavailable",
            "available_strategies": [s.value for s in SearchStrategy],
            "available_presets": ["balanced", "fast", "comprehensive"]
        }

    async def get_search_suggestions(self, text: str) -> List[str]:
        """Get search suggestions based on input text."""
        strategy = self._detect_search_strategy(text)
        
        suggestions = []
        if strategy == SearchStrategy.ACADEMIC:
            suggestions = [
                "Bagaimana cara melihat jadwal kuliah?",
                "Berapa SKS minimal per semester?",
                "Siapa dosen pengampu mata kuliah X?"
            ]
        elif strategy == SearchStrategy.ADMINISTRATIVE:
            suggestions = [
                "Bagaimana cara mendaftar ulang?",
                "Berapa biaya SPP semester ini?",
                "Dokumen apa saja yang diperlukan untuk pendaftaran?"
            ]
        elif strategy == SearchStrategy.FACILITY:
            suggestions = [
                "Di mana lokasi perpustakaan pusat?",
                "Jam operasional laboratorium komputer?",
                "Fasilitas apa saja yang tersedia di kampus?"
            ]
        else:
            suggestions = [
                "Informasi umum tentang Universitas Gunadarma",
                "Kontak dan alamat kampus",
                "Program studi yang tersedia"
            ]
            
        return suggestions

    async def multi_strategy_search(self, question: str) -> Dict[str, SearchResponse]:
        """Perform search with multiple strategies for comparison."""
        strategies = [
            SearchStrategy.ACADEMIC,
            SearchStrategy.ADMINISTRATIVE, 
            SearchStrategy.FACILITY,
            SearchStrategy.QUICK
        ]
        
        results = {}
        for strategy in strategies:
            query = SearchQuery(text=question, strategy=strategy)
            response = await self.search(query)
            results[strategy.value] = response
            
        return results

    def _detect_search_strategy(self, question: str) -> SearchStrategy:
        """Detect the best search strategy based on question content."""
        question_lower = question.lower()
        
        # Count keyword matches for each strategy
        strategy_scores = {}
        for strategy, keywords in self._strategy_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                strategy_scores[strategy] = score
        
        # Return strategy with highest score, or GENERAL as default
        if strategy_scores:
            return max(strategy_scores.keys(), key=lambda k: strategy_scores[k])
        
        return SearchStrategy.SMART  # Default to smart strategy


class ChatbotService:
    """Service for handling chatbot operations."""
    
    def __init__(self, search_service: SearchServiceInterface):
        self.search_service = search_service
        self.hybrid_available = True  # Set based on availability
    
    async def process_message(
        self, 
        message: str, 
        strategy: Optional[SearchStrategy] = None
    ) -> str:
        """Process user message and return formatted response."""
        try:
            query = SearchQuery(text=message, strategy=strategy)
            response = await self.search_service.search(query)
            
            if response.error:
                return f"❌ **Error:** {response.error_message}"
            
            # Format response
            formatted_response = self._format_response(response)
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"❌ **Error:** Terjadi kesalahan saat memproses pertanyaan Anda: {str(e)}"
    
    def _format_response(self, response: SearchResponse) -> str:
        """Format search response for display."""
        answer = response.answer
        
        if response.source_urls:
            sources_section = "\n\n**📚 Sumber:**\n"
            for i, url in enumerate(response.source_urls[:3], 1):
                sources_section += f"{i}. {url}\n"
            answer += sources_section
        
        return answer
