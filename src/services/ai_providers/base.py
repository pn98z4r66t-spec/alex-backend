"""
Base AI Provider Interface
Abstract base class for AI providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AI provider
        
        Args:
            config: Provider configuration
        """
        self.config = config
    
    @abstractmethod
    def chat(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat message to the AI
        
        Args:
            prompt: The prompt/message to send
            model: Optional model override
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict containing response and metadata
        """
        pass
    
    @abstractmethod
    def stream_chat(self, prompt: str, model: Optional[str] = None, **kwargs):
        """
        Stream chat responses
        
        Args:
            prompt: The prompt/message to send
            model: Optional model override
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Response chunks
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the AI provider is available
        
        Returns:
            True if available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_models(self) -> list:
        """
        Get list of available models
        
        Returns:
            List of model names
        """
        pass
    
    def format_response(self, raw_response: Any) -> Dict[str, Any]:
        """
        Format provider-specific response to standard format
        
        Args:
            raw_response: Raw response from provider
            
        Returns:
            Standardized response dict
        """
        return {
            'response': str(raw_response),
            'model': 'unknown',
            'provider': self.__class__.__name__,
            'success': True
        }

