"""
Gunadarma University RAG Chatbot - Clean Architecture Implementation

This is the main entry point for the Chainlit chatbot application using clean architecture.
All business logic is properly separated into layers with dependency injection.
"""

import os
import logging
from typing import Optional

import chainlit as cl
from dotenv import load_dotenv

from src import app
from src.domain.enums import SearchStrategy

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@cl.set_chat_profiles
async def setup_chat_profile():
    """Configure the chat profile with welcome message, avatar, and starter questions."""
    try:
        chat_profile_config = app.get_chat_profile_config()
        profile_data = chat_profile_config.create_chat_profile(app.is_hybrid_available())
        
        starters = []
        for starter_data in profile_data['starters']:
            starter = cl.Starter(
                label=starter_data['label'],
                message=starter_data['message'],
                icon=starter_data['icon']
            )
            starters.append(starter)
        
        profile = cl.ChatProfile(
            name=profile_data['name'],
            markdown_description=profile_data['description'],
            icon=profile_data['icon'],
            starters=starters,
        )
        
        return [profile]
    except Exception as e:
        logger.error(f"Error setting up chat profile: {e}")
        return [
            cl.ChatProfile(
                name="Chatbot UG",
                markdown_description="**Chatbot Universitas Gunadarma** - Mode Darurat",
                icon="/public/favicon.png",
                starters=[],
            )
        ]


@cl.on_message
async def handle_user_message(message: cl.Message):
    """Handle incoming user messages through the chat controller."""
    try:
        # Add detailed logging for debugging Docker issues
        logger.info(f"Received message: '{message.content}' (type: {type(message.content)}, length: {len(message.content) if message.content else 0})")
        
        # Validate message content early
        if not message.content or not isinstance(message.content, str) or not message.content.strip():
            logger.warning(f"Invalid message content received: {repr(message.content)}")
            error_message = "❌ **Error:** Pesan tidak boleh kosong. Silakan masukkan pertanyaan Anda."
            await cl.Message(content=error_message, author="Assistant").send()
            return
        
        chat_controller = app.get_chat_controller()
        
        # Always use hybrid search and show sources
        search_mode = SearchStrategy.HYBRID.value
        show_sources = True
        
        async with cl.Step(name="RAG System", type="run") as step:
            step.input = message.content
            
            try:
                # Process message through controller with hybrid search and sources enabled
                response_text = await chat_controller.process_message(
                    message.content, 
                    search_strategy=search_mode,
                    show_sources=show_sources
                )
                
                # Check if response indicates an error
                if "❌" in response_text or "Error" in response_text:
                    step.is_error = True
                    step.output = "Terjadi kesalahan dalam pencarian"
                else:
                    step.output = "Pencarian berhasil dengan Hybrid Search"
                    
            except Exception as e:
                logger.error(f"Error in message handling: {e}")
                response_text = f"❌ **Error:** Terjadi kesalahan yang tidak terduga: {str(e)}"
                step.is_error = True
                step.output = response_text
        
        await cl.Message(content=response_text, author="Assistant").send()        
    except Exception as e:
        logger.error(f"Critical error in message handling: {e}")
        error_message = f"❌ **System Error:** Terjadi kesalahan sistem yang tidak terduga. Silakan coba lagi atau hubungi administrator."
        await cl.Message(content=error_message, author="Assistant").send()


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session."""
    logger.info("New chat session started - Using Hybrid Search with sources enabled by default")
    
    if not app.is_hybrid_available():
        warning_message = """
⚠️ **Peringatan:** Sistem sedang berjalan dalam mode kompatibilitas. 
Hybrid Search tidak tersedia saat ini.

Silakan lanjutkan dengan mengetikkan pertanyaan Anda.
        """
        await cl.Message(content=warning_message, author="System").send()


@cl.on_chat_end
async def on_chat_end():
    """Clean up when chat session ends."""
    logger.info("Chat session ended")


if __name__ == "__main__":
    print("🚀 Gunadarma RAG Chatbot - Clean Architecture")
    print("📁 Struktur: Domain → Application → Infrastructure → Presentation")
    print("🔧 Untuk menjalankan: chainlit run app.py -w")
    print("🌐 Mode:", "Hybrid Search" if app.is_hybrid_available() else "Compatibility Mode")
