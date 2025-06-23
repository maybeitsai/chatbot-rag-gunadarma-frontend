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
        strategy = query.strategy
        if strategy is None:
            strategy = self._detect_search_strategy(query.text)
            
        logger.info(f"Using search strategy: {strategy.value}")
        
        response = await self.client.search(query.text)
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
        
        strategy_scores = {}
        for strategy, keywords in self._strategy_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                strategy_scores[strategy] = score
        
        if strategy_scores:
            return max(strategy_scores.keys(), key=lambda k: strategy_scores[k])
        
        return SearchStrategy.SMART


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
            if search_options and 'strategy' in search_options:
                strategy_str = search_options['strategy']
                if isinstance(strategy_str, str):
                    try:
                        strategy = SearchStrategy(strategy_str)
                    except ValueError:
                        logger.warning(f"Unknown strategy: {strategy_str}, using default")
                        strategy = None
            
            query = SearchQuery(text=message, strategy=strategy)
            response = await self.search_service.search(query)
            
            if response.error:
                return f"❌ **Error:** {response.error_message}"
            
            formatted_response = self._format_response(response, search_options)
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"❌ **Error:** Terjadi kesalahan saat memproses pertanyaan Anda: {str(e)}"
    
    def _format_response(self, response: SearchResponse, search_options: Optional[Dict[str, Any]] = None) -> str:
        """Format search response for display."""
        answer = response.answer
        
        show_sources = True
        if search_options:
            show_sources = search_options.get('show_sources', True)
        
        detailed_response = False
        if search_options:
            detailed_response = search_options.get('detailed_response', False)
        
        # Apply response formatting rules:
        # Only show sources if the answer is not the standard "not available" message
        standard_message = "Maaf, informasi mengenai hal tersebut tidak tersedia dalam data kami."
        
        if detailed_response and hasattr(response, 'metadata'):
            if response.metadata:
                answer += f"\n\n**🔍 Detail Pencarian:**\n"
                if 'search_type' in response.metadata:
                    answer += f"- Mode: {response.metadata['search_type']}\n"
                if 'confidence_score' in response.metadata:
                    answer += f"- Skor Kepercayaan: {response.metadata['confidence_score']:.2f}\n"
        
        # Only add sources if it's not the standard "not available" message
        if show_sources and response.source_urls and answer.strip() != standard_message:
            sources_section = "\n\n**📚 Sumber:**\n"
            for i, url in enumerate(response.source_urls[:3], 1):
                sources_section += f"{i}. {url}\n"
            answer += sources_section
        
        return answer
