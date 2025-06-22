"""Core exceptions - Application exceptions."""


class ChatbotException(Exception):
    """Base exception for chatbot application."""
    pass


class SearchException(ChatbotException):
    """Exception raised during search operations."""
    pass


class ConfigurationException(ChatbotException):
    """Exception raised for configuration errors."""
    pass


class ApiException(ChatbotException):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ValidationException(ChatbotException):
    """Exception raised for validation errors."""
    pass
