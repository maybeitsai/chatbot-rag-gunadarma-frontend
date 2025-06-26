"""Infrastructure API implementations."""

import os
import logging
from typing import Dict, Any, Optional, List
import asyncio
import time
import httpx

from ..core import ApiClientInterface, ApiException
from ..domain import SearchResponse, SearchQuery, SearchResult, ResponseStatus, BatchRequest, BatchResponse, BatchResult
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

    async def search(self, query: str, use_hybrid: bool = True) -> SearchResponse:
        """Perform search via API using backend format."""
        # Sanitize input
        sanitized_query = self._sanitize_input(query)
        if not sanitized_query:
            return self._create_error_response("Pertanyaan tidak boleh kosong.")

        # Create search query object
        search_query = SearchQuery(text=sanitized_query)

        # Attempt request with retries
        for attempt in range(self.config.max_retries):
            try:
                response_data = await self._make_search_request(sanitized_query, use_hybrid)
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

    async def batch_search(self, batch_request: BatchRequest) -> BatchResponse:
        """Perform batch search via API."""
        start_time = time.time()
        
        try:
            # Make batch request with retries
            for attempt in range(self.config.max_retries):
                try:
                    response_data = await self._make_batch_request(batch_request)
                    processing_time = time.time() - start_time
                    return self._create_batch_response(response_data, processing_time)
                
                except ApiException as e:
                    if attempt == self.config.max_retries - 1:
                        return self._create_batch_error_response(
                            batch_request, e.args[0], time.time() - start_time
                        )
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                
                except Exception as e:
                    if attempt == self.config.max_retries - 1:
                        return self._create_batch_error_response(
                            batch_request, 
                            f"Terjadi kesalahan yang tidak terduga: {str(e)}", 
                            time.time() - start_time
                        )
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
            
            return self._create_batch_error_response(
                batch_request, 
                "Gagal terhubung setelah beberapa percobaan.", 
                time.time() - start_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return self._create_batch_error_response(
                batch_request, 
                f"Kesalahan batch processing: {str(e)}", 
                processing_time
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

    async def _make_search_request(self, question: str, use_hybrid: bool = True) -> Dict[str, Any]:
        """Make HTTP request to search API using backend format."""
        payload = {
            "question": question,
            "use_cache": True,
            "use_hybrid": use_hybrid
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

    async def _make_batch_request(self, batch_request: BatchRequest) -> Dict[str, Any]:
        """Make HTTP request to batch API."""
        payload = {
            "questions": batch_request.questions,
            "use_cache": batch_request.use_cache,
            "use_hybrid": batch_request.use_hybrid
        }

        async with httpx.AsyncClient(timeout=self.config.timeout * 2) as client:  # Extended timeout for batch
            try:
                response = await client.post(
                    self._batch_endpoint,
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

    def _create_batch_response(self, data: Dict[str, Any], processing_time: float) -> BatchResponse:
        """Create batch response from API data."""
        results = []
        
        for result_data in data.get("results", []):
            batch_result = BatchResult(
                answer=result_data.get("answer", ""),
                source_urls=result_data.get("source_urls", []),
                status=result_data.get("status", "success"),
                source_count=result_data.get("source_count", 0),
                response_time=result_data.get("response_time", 0.0),
                cached=result_data.get("cached", False),
                cache_type=result_data.get("cache_type"),
                search_type=result_data.get("search_type")
            )
            results.append(batch_result)
        
        return BatchResponse(
            results=results,
            total_questions=data.get("total_questions", len(results)),
            processing_time=processing_time
        )

    def _create_batch_error_response(self, batch_request: BatchRequest, error_message: str, processing_time: float) -> BatchResponse:
        """Create error batch response."""
        error_results = []
        
        for question in batch_request.questions:
            error_result = BatchResult(
                answer=f"Error: {error_message}",
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
            processing_time=processing_time
        )

    def _apply_response_rules(self, answer: str, source_urls: List[str]) -> tuple[str, List[str]]:
        """
        Apply response handling rules as specified:
        1. If response is empty or only spaces, return standard message without sources
        2. If response is already the standard message, return as-is without sources
        3. For other responses, return as-is with sources
        """
        # Check if answer is empty or only whitespace
        if not answer or answer.strip() == "":
            return "Maaf, informasi mengenai hal tersebut tidak tersedia dalam data kami.", []
        
        # Check if answer is already the standard "not available" message
        standard_message = "Maaf, informasi mengenai hal tersebut tidak tersedia dalam data kami."
        if answer.strip() == standard_message:
            return standard_message, []
        
        # For all other responses, return as-is with sources
        return answer, source_urls

    def _create_success_response(self, query: SearchQuery, data: Dict[str, Any]) -> SearchResponse:
        """Create success response from API data using backend response format."""
        # Backend response format:
        # {
        #   "answer": "string",
        #   "source_urls": ["string"],
        #   "status": "string",
        #   "source_count": 0,
        #   "response_time": 0,
        #   "cached": false,
        #   "cache_type": "string",
        #   "search_type": "string"
        # }
        
        # Handle response according to specified rules
        answer = data.get("answer", "")
        source_urls = data.get("source_urls", [])
        
        # Apply response handling rules
        processed_answer, processed_sources = self._apply_response_rules(answer, source_urls)

        response = SearchResponse(
            query=query,
            answer=processed_answer,
            results=[],  # Backend doesn't provide detailed results
            status=ResponseStatus.SUCCESS,
            source_urls=processed_sources,
            response_time=data.get("response_time", 0.0),
            cached=data.get("cached", False),
            cache_type=data.get("cache_type"),
            search_type=data.get("search_type"),
            source_count=data.get("source_count", len(processed_sources))
        )

        return response
