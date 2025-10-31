"""
OpenAI Provider
Implements AI provider interface for OpenAI ChatGPT API
"""
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from src.utils.errors import APIError

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """OpenAI ChatGPT API provider"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider
        
        Args:
            config: Configuration dict with:
                - api_key: OpenAI API key
                - default_model: Default model (e.g., 'gpt-4', 'gpt-3.5-turbo')
                - timeout: Request timeout in seconds
                - temperature: Sampling temperature (0-2)
                - max_tokens: Maximum tokens in response
        """
        self.api_key = config.get('api_key')
        self.default_model = config.get('default_model', 'gpt-3.5-turbo')
        self.timeout = config.get('timeout', 30)
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2048)
        
        if not self.api_key:
            raise ValueError('OpenAI API key is required')
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        logger.info(f'OpenAI provider initialized with model: {self.default_model}')
    
    def chat(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat message to OpenAI
        
        Args:
            prompt: The prompt/message
            model: Optional model override
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Response dict with:
                - response: The AI response text
                - model: Model used
                - usage: Token usage information
                - finish_reason: Why the model stopped generating
        """
        model_name = model or self.default_model
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        timeout = kwargs.get('timeout', self.timeout)
        
        try:
            logger.info(f'Sending request to OpenAI (model: {model_name})')
            
            # Call OpenAI Chat Completions API
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )
            
            # Extract response
            message = response.choices[0].message
            content = message.content
            
            # Build response dict
            result = {
                'response': content,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'finish_reason': response.choices[0].finish_reason
            }
            
            logger.info(f'OpenAI response received (tokens: {response.usage.total_tokens})')
            return result
            
        except Exception as e:
            logger.error(f'OpenAI API error: {str(e)}')
            raise APIError(f'OpenAI API error: {str(e)}', 500)
    
    def chat_with_history(self, messages: list, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat with conversation history to OpenAI
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                      Example: [{"role": "user", "content": "Hello"}]
            model: Optional model override
            **kwargs: Additional parameters
            
        Returns:
            Response dict (same format as chat())
        """
        model_name = model or self.default_model
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        timeout = kwargs.get('timeout', self.timeout)
        
        try:
            logger.info(f'Sending conversation to OpenAI (model: {model_name}, messages: {len(messages)})')
            
            # Call OpenAI Chat Completions API with history
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )
            
            # Extract response
            message = response.choices[0].message
            content = message.content
            
            # Build response dict
            result = {
                'response': content,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'finish_reason': response.choices[0].finish_reason
            }
            
            logger.info(f'OpenAI response received (tokens: {response.usage.total_tokens})')
            return result
            
        except Exception as e:
            logger.error(f'OpenAI API error: {str(e)}')
            raise APIError(f'OpenAI API error: {str(e)}', 500)
    
    def is_available(self) -> bool:
        """
        Check if OpenAI API is available
        
        Returns:
            True if available, False otherwise
        """
        try:
            # Try a simple API call to check availability
            response = self.client.models.list()
            return True
        except Exception as e:
            logger.error(f'OpenAI availability check failed: {str(e)}')
            return False
    
    def list_models(self) -> list:
        """
        List available OpenAI models
        
        Returns:
            List of model IDs
        """
        try:
            response = self.client.models.list()
            models = [model.id for model in response.data]
            return models
        except Exception as e:
            logger.error(f'Failed to list models: {str(e)}')
            return []

