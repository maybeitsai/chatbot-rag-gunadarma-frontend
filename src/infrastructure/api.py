"""Infrastructure API implementations."""

import os
import logging
from typing import Dict, Any, Optional, List
import asyncio
import httpx

from ..core import ApiClientInterface, ApiException
from ..domain import SearchResponse, SearchQuery, SearchResult, ResponseStatus
from .config import ApiConfig


logger = logging.getLogger(__name__)


class RAGApiClient(ApiClientInterface):
    """
    Enhanced API client with hybrid search support.
    
    Provides comprehensive search functionality with different search types,
    configurable parameters, and robust error handling.
    """

    def __init__(self, config: Optional[ApiConfig] = None):
        """Initialize the enhanced API client."""
        if config is None:
            config = ApiConfig.from_env()

        self.config = config
        self._ask_endpoint = f"{self.config.base_url}/api/v1/ask"
        self._batch_endpoint = f"{self.config.base_url}/api/v1/batch"
        self._health_endpoint = f"{self.config.base_url}/api/v1/health"

    async def search(self, query: str) -> SearchResponse:
        """Perform search via API."""
        # Sanitize input
        sanitized_query = self._sanitize_input(query)
        if not sanitized_query:
            return self._create_error_response("Pertanyaan tidak boleh kosong.")

        # Create search query object
        search_query = SearchQuery(text=sanitized_query)

        # Attempt request with retries
        for attempt in range(self.config.max_retries):
            try:
                response_data = await self._make_search_request(sanitized_query)
                return self._create_success_response(search_query, response_data)

            except ApiException as e:
                if attempt == self.config.max_retries - 1:
                    return self._create_error_response(e.args[0])
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))

            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    return self._create_error_response(
                        f"Terjadi kesalahan yang tidak terduga: {str(e)}"
                    )
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))

        return self._create_error_response(
            "Gagal terhubung setelah beberapa percobaan."
        )

    def health_check(self) -> bool:
        """Check API health."""
        try:
            import requests
            response = requests.get(
                self._health_endpoint, 
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    async def _make_search_request(self, question: str) -> Dict[str, Any]:
        """Make HTTP request to search API."""
        payload = {
            "question": question,
            "search_type": "hybrid",
            "max_results": 10
        }

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.post(
                    self._ask_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise ApiException(
                    f"HTTP error {e.response.status_code}: {e.response.text}",
                    e.response.status_code
                )
            except httpx.RequestError as e:
                raise ApiException(f"Network error: {str(e)}")

    def _sanitize_input(self, text: str) -> str:
        """Sanitize user input."""
        if not text or not isinstance(text, str):
            return ""
        return text.strip()

    def _create_error_response(self, error_message: str) -> SearchResponse:
        """Create error response."""
        dummy_query = SearchQuery(text="")
        return SearchResponse(
            query=dummy_query,
            answer="",
            status=ResponseStatus.ERROR,
            error_message=error_message
        )

    def _create_success_response(self, query: SearchQuery, data: Dict[str, Any]) -> SearchResponse:
        """Create success response from API data."""
        # Extract results
        results = []
        for item in data.get("sources", []):
            result = SearchResult(
                content=item.get("content", ""),
                source_url=item.get("source_url", ""),
                title=item.get("title", ""),
                relevance_score=item.get("relevance_score", 0.0),
                metadata=item.get("metadata", {})
            )
            results.append(result)

        response = SearchResponse(
            query=query,
            answer=data.get("answer", ""),
            results=results,
            status=ResponseStatus.SUCCESS,
            source_urls=data.get("source_urls", []),
            response_time=data.get("response_time", 0.0),
            cached=data.get("cached", False),
            cache_type=data.get("cache_type"),
            search_type=data.get("search_type"),
            source_count=len(data.get("source_urls", []))
        )

        return response
