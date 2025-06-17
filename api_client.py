"""
API client for communicating with the RAG backend service.

This module provides a robust HTTP client for sending questions to the FastAPI
backend and handling responses with proper error handling and retry logic.
"""

import os
from typing import Dict, Any, Optional
import asyncio
from dataclasses import dataclass

import httpx

from utils.cache import cached_async, app_cache, sanitize_input


@dataclass
class ApiConfig:
    """Configuration for API client."""

    base_url: str
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0


class ApiError(Exception):
    """Custom exception for API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class RAGApiClient:
    """
    Client for interacting with the RAG FastAPI backend.

    Provides methods to send questions and receive responses with proper
    error handling, retries, and response formatting.
    """

    def __init__(self, config: Optional[ApiConfig] = None):
        """
        Initialize the API client.

        Args:
            config: API configuration object. If None, creates default config.
        """
        if config is None:
            base_url = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")
            config = ApiConfig(base_url=base_url)

        self.config = config
        self._ask_endpoint = f"{self.config.base_url}/ask"

    @cached_async(ttl=600, cache_instance=app_cache)  # Cache for 10 minutes
    async def get_rag_response(self, question: str) -> Dict[str, Any]:
        """
        Send a question to the RAG backend and return the response.

        Args:
            question: User's question to send to the backend

        Returns:
            Dictionary containing the response or error information
        """
        # Sanitize input
        sanitized_question = sanitize_input(question)

        if not sanitized_question:
            return self._create_error_response("Pertanyaan tidak boleh kosong.")

        for attempt in range(self.config.max_retries):
            try:
                response = await self._make_request(sanitized_question)
                return response

            except ApiError as e:
                if attempt == self.config.max_retries - 1:
                    return self._create_error_response(e.message)

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

    async def _make_request(self, question: str) -> Dict[str, Any]:
        """
        Make HTTP request to the backend API.

        Args:
            question: User's question

        Returns:
            Response from the API

        Raises:
            ApiError: If the request fails
        """
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                payload = {"question": question}
                response = await client.post(self._ask_endpoint, json=payload)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                error_message = self._format_http_error(e)
                raise ApiError(error_message, e.response.status_code)

            except httpx.RequestError as e:
                error_message = (
                    f"Tidak dapat terhubung ke server. "
                    f"Pastikan backend berjalan di {self.config.base_url}."
                )
                raise ApiError(error_message)

    def _format_http_error(self, error: httpx.HTTPStatusError) -> str:
        """
        Format HTTP status error into user-friendly message.

        Args:
            error: HTTP status error

        Returns:
            Formatted error message
        """
        status_code = error.response.status_code

        if status_code == 500:
            return "Terjadi kesalahan pada server. Silakan coba lagi nanti."
        elif status_code == 502 or status_code == 503:
            return "Server sedang tidak tersedia. Silakan coba lagi nanti."
        elif status_code == 404:
            return "Endpoint tidak ditemukan. Periksa konfigurasi backend."
        else:
            return f"Terjadi kesalahan pada server: {status_code}. Silakan coba lagi nanti."

    @staticmethod
    def _create_error_response(message: str) -> Dict[str, Any]:
        """
        Create standardized error response dictionary.

        Args:
            message: Error message

        Returns:
            Error response dictionary
        """
        return {
            "error": True,
            "message": message,
        }

    def health_check(self) -> bool:
        """
        Check if the backend service is available.

        Returns:
            True if service is available, False otherwise
        """
        # This could be implemented to ping a health endpoint
        # For now, we'll just check if the base URL is configured
        return bool(self.config.base_url)


# Backward compatibility function
async def get_rag_response(question: str) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.

    Args:
        question: User's question

    Returns:
        Response dictionary
    """
    client = RAGApiClient()
    return await client.get_rag_response(question)
