"""
Chainlit application for Gunadarma University RAG chatbot.

This module provides a conversational interface for students to get information
about Gunadarma University including academic information, administration procedures,
and campus facilities.
"""

import random
from collections import defaultdict
from typing import List, Dict

import chainlit as cl
from dotenv import load_dotenv

from api_client import RAGApiClient
from utils.cache import format_response_sources

# Load environment variables at startup
load_dotenv()

# Initialize API client
api_client = RAGApiClient()

# --- STARTER QUESTIONS CONFIGURATION ---
from config.starter_questions import (
    get_all_starter_questions,
    group_starters_by_icon,
    select_random_starters_per_category,
)


class ChatbotResponseHandler:
    """Handles chatbot responses and formatting."""

    DEFAULT_ERROR_MESSAGE = (
        "Maaf, saya tidak dapat menemukan jawaban untuk pertanyaan Anda."
    )

    def __init__(self, api_client: RAGApiClient):
        self.api_client = api_client

    async def process_user_message(self, message_content: str) -> str:
        """
        Process user message and return formatted response.

        Args:
            message_content: User's message content

        Returns:
            Formatted response string
        """
        response = await self.api_client.get_rag_response(message_content)

        if response.get("error"):
            return response["message"]

        return self._format_successful_response(response)

    def _format_successful_response(self, response: dict) -> str:
        """
        Format successful API response with answer and sources.

        Args:
            response: API response dictionary

        Returns:
            Formatted response string
        """
        answer = response.get("answer", self.DEFAULT_ERROR_MESSAGE)
        source_urls = response.get("source_urls", [])

        if not source_urls:
            return answer

        sources_section = format_response_sources(source_urls)
        return f"{answer}{sources_section}"


# Initialize response handler
response_handler = ChatbotResponseHandler(api_client)


@cl.set_chat_profiles
async def setup_chat_profile():
    """
    Configure the chat profile with welcome message, avatar, and starter questions.

    Returns:
        List containing the configured chat profile
    """
    all_starters = get_all_starter_questions()
    grouped_starters = group_starters_by_icon(all_starters)
    selected_starters = select_random_starters_per_category(grouped_starters)

    return [
        cl.ChatProfile(
            name="Chatbot UG",
            markdown_description="""
## &emsp; **Chatbot Universitas Gunadarma** &emsp;

&emsp; Siap membantu seputar info akademik Universitas Gunadarma. &emsp;
""",
            icon="/public/favicon.png",
            starters=selected_starters,
        )
    ]


@cl.on_message
async def handle_user_message(message: cl.Message):
    """
    Handle incoming user messages and provide responses.

    Args:
        message: User message from Chainlit
    """
    async with cl.Step(name="Context", type="run") as step:
        step.input = message.content

        try:
            response_text = await response_handler.process_user_message(message.content)

            # Check if response indicates an error
            if (
                "Terjadi kesalahan" in response_text
                or "Tidak dapat terhubung" in response_text
            ):
                step.is_error = True
                step.output = response_text
            else:
                step.output = "Jawaban berhasil ditemukan."

        except Exception as e:
            response_text = f"Terjadi kesalahan yang tidak terduga: {str(e)}"
            step.is_error = True
            step.output = response_text

    await cl.Message(content=response_text, author="Assistant").send()
