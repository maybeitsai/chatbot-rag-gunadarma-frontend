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
from chainlit.input_widget import Select, Switch

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
        chat_controller = app.get_chat_controller()
        
        search_mode = cl.user_session.get("search_mode", SearchStrategy.HYBRID.value if app.is_hybrid_available() else SearchStrategy.SEMANTIC.value)
        show_sources = cl.user_session.get("show_sources", True)
        detailed_response = cl.user_session.get("detailed_response", False)
        
        mode_names = {
            SearchStrategy.HYBRID.value: "Hybrid Search",
            SearchStrategy.SEMANTIC.value: "Semantic Search", 
            SearchStrategy.KEYWORD.value: "Keyword Search",
            SearchStrategy.SMART.value: "Smart Search",
            SearchStrategy.ACADEMIC.value: "Academic Search",
            SearchStrategy.ADMINISTRATIVE.value: "Administrative Search", 
            SearchStrategy.FACILITY.value: "Facility Search",
            SearchStrategy.QUICK.value: "Quick Search"
        }
        
        step_name = mode_names.get(search_mode, search_mode)
        
        async with cl.Step(name=step_name, type="run") as step:
            step.input = message.content
            
            try:
                # Process message through controller with selected search mode
                response_text = await chat_controller.process_message(
                    message.content, 
                    search_strategy=search_mode,
                    show_sources=show_sources,
                    detailed_response=detailed_response
                )
                
                # Check if response indicates an error
                if "❌" in response_text or "Error" in response_text:
                    step.is_error = True
                    step.output = f"Terjadi kesalahan dalam pencarian dengan {step_name}"
                else:
                    step.output = f"Pencarian berhasil dengan {step_name}"
                    
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
    """Initialize chat session and setup search mode settings."""
    logger.info("New chat session started")
    
    await setup_search_settings()
    
    if not app.is_hybrid_available():
        warning_message = """
⚠️ **Peringatan:** Sistem sedang berjalan dalam mode kompatibilitas. 
Beberapa fitur mungkin tidak tersedia.

Silakan lanjutkan dengan mengetikkan pertanyaan Anda.
        """
        await cl.Message(content=warning_message, author="System").send()


async def setup_search_settings():
    """Setup search mode settings for the chat."""
    search_options = []
    search_values = []
    
    if app.is_hybrid_available():
        search_options = [
            "Hybrid Search",
            "Semantic Search", 
            "Keyword Search",
            "Smart Search",
            "Academic Search", 
            "Administrative Search",
            "Facility Search",
            "Quick Search"
        ]
        search_values = [
            SearchStrategy.HYBRID.value,
            SearchStrategy.SEMANTIC.value,
            SearchStrategy.KEYWORD.value, 
            SearchStrategy.SMART.value,
            SearchStrategy.ACADEMIC.value,
            SearchStrategy.ADMINISTRATIVE.value,
            SearchStrategy.FACILITY.value,
            SearchStrategy.QUICK.value
        ]
        initial_index = 0  # Default to Hybrid
    else:
        search_options = [
            "Semantic Search",
            "Keyword Search", 
            "Quick Search"
        ]
        search_values = [
            SearchStrategy.SEMANTIC.value,
            SearchStrategy.KEYWORD.value,
            SearchStrategy.QUICK.value
        ]
        initial_index = 0  # Default to Semantic
    
    settings = await cl.ChatSettings(
        [
            Select(
                id="search_mode",
                label="🔍 Mode Pencarian",
                values=search_options,
                initial_index=initial_index,
                description="Pilih mode pencarian yang sesuai dengan kebutuhan Anda"
            ),
            Switch(
                id="show_sources", 
                label="📚 Tampilkan Sumber",
                initial=True,
                description="Tampilkan sumber referensi dalam jawaban"
            ),
            Switch(
                id="detailed_response",                label="📝 Jawaban Detail", 
                initial=False,
                description="Berikan jawaban yang lebih detail dan komprehensif"
            )
        ]
    ).send()
    
    cl.user_session.set("search_mode", search_values[initial_index])
    cl.user_session.set("show_sources", True)
    cl.user_session.set("detailed_response", False)


@cl.on_settings_update
async def on_settings_update(settings):
    """Handle search settings updates."""
    logger.info(f"Settings updated: {settings}")    
    cl.user_session.set("search_mode", settings.get("search_mode", SearchStrategy.HYBRID.value))
    cl.user_session.set("show_sources", settings.get("show_sources", True))
    cl.user_session.set("detailed_response", settings.get("detailed_response", False))
    
    search_mode = settings.get("search_mode", SearchStrategy.HYBRID.value)
    mode_names = {
        SearchStrategy.HYBRID.value: "Hybrid Search",
        SearchStrategy.SEMANTIC.value: "Semantic Search", 
        SearchStrategy.KEYWORD.value: "Keyword Search",
        SearchStrategy.SMART.value: "Smart Search",
        SearchStrategy.ACADEMIC.value: "Academic Search",
        SearchStrategy.ADMINISTRATIVE.value: "Administrative Search", 
        SearchStrategy.FACILITY.value: "Facility Search",
        SearchStrategy.QUICK.value: "Quick Search"
    }    
    mode_name = mode_names.get(search_mode, search_mode)
    show_sources = "enabled" if settings.get("show_sources", True) else "disabled"
    detailed = "enabled" if settings.get("detailed_response", False) else "disabled"
    logger.info(f"Search mode updated to: {mode_name}, Show sources: {show_sources}, Detailed response: {detailed}")


@cl.on_chat_end
async def on_chat_end():
    """Clean up when chat session ends."""
    logger.info("Chat session ended")


if __name__ == "__main__":
    print("🚀 Gunadarma RAG Chatbot - Clean Architecture")
    print("📁 Struktur: Domain → Application → Infrastructure → Presentation")
    print("🔧 Untuk menjalankan: chainlit run app.py -w")
    print("🌐 Mode:", "Hybrid Search" if app.is_hybrid_available() else "Legacy API")
