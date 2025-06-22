"""Main module - Clean architecture bootstrap."""

import os
import logging
from typing import Optional

# Infrastructure
from .infrastructure import ApiConfig, RAGApiClient, SimpleCache

# Application
from .application import SearchService, ChatbotService, SearchUseCase, ChatUseCase, HealthCheckUseCase

# Presentation  
from .presentation import ChatController, ResponseFormatter, ChatProfileConfig

# Domain
from .domain import SearchStrategy

# Core
from .core import ChatbotException


logger = logging.getLogger(__name__)


class Application:
    """Main application class - Dependency injection container."""
    
    def __init__(self):
        self._setup_logging()
        self._initialize_dependencies()
    
    def _setup_logging(self):
        """Setup application logging."""
        logging.basicConfig(level=logging.INFO)
    
    def _initialize_dependencies(self):
        """Initialize all dependencies using dependency injection."""
        try:
            # Infrastructure layer
            self.api_config = ApiConfig.from_env()
            self.api_client = RAGApiClient(self.api_config)
            self.cache = SimpleCache()
            
            # Application layer
            self.search_service = SearchService(self.api_config)
            self.chatbot_service = ChatbotService(self.search_service)
            
            # Use cases
            self.search_use_case = SearchUseCase(self.search_service)
            self.chat_use_case = ChatUseCase(self.chatbot_service)
            self.health_check_use_case = HealthCheckUseCase(self.search_service)
            
            # Presentation layer
            self.formatter = ResponseFormatter(show_debug_info=False)
            self.chat_controller = ChatController(
                self.chat_use_case,
                self.search_use_case,
                self.health_check_use_case,
                self.formatter
            )
            
            self.hybrid_available = True
            logger.info("✅ Application initialized successfully with hybrid search")
            
        except ImportError as e:
            logger.warning(f"⚠️ Hybrid search not available: {e}")
            # Fallback initialization
            self._initialize_fallback()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize application: {e}")
            raise ChatbotException(f"Application initialization failed: {e}")
    
    def _initialize_fallback(self):
        """Initialize with fallback configuration."""
        # Minimal fallback setup
        self.api_config = ApiConfig.from_env()
        self.formatter = ResponseFormatter()
        self.hybrid_available = False
        
        logger.info("⚠️ Application initialized with fallback configuration")
    
    def get_chat_controller(self) -> ChatController:
        """Get the chat controller."""
        return self.chat_controller
    
    def get_chat_profile_config(self) -> 'ChatProfileConfig':
        """Get chat profile configuration."""
        return ChatProfileConfig()
    
    def is_hybrid_available(self) -> bool:
        """Check if hybrid search is available."""
        return self.hybrid_available


# Global application instance
app = Application()
