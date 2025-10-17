"""
Ollama AI Provider
Implementation for Ollama local AI service
"""
import requests
import logging
from typing import Dict, Any, Optional
from .base import AIProvider
from src.utils.errors import APIError

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """Ollama AI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama provider
        
        Args:
            config: Configuration dict with 'api_url' and 'default_model'
        """
        super().__init__(config)
        self.api_url = config.get('api_url', 'http://localhost:11434')
        self.default_model = config.get('default_model', 'phi3')
        self.timeout = config.get('timeout', 30)
    
    def chat(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat message to Ollama
        
        Args:
            prompt: The prompt/message to send
            model: Optional model override
            **kwargs: Additional parameters (temperature, top_p, etc.)
            
        Returns:
            Dict containing response and metadata
            
        Raises:
            APIError: If the request fails
        """
        model_name = model or self.default_model
        timeout = kwargs.get('timeout', self.timeout)
        
        try:
            response = requests.post(
                f'{self.api_url}/api/generate',
                json={
                    'model': model_name,
                    'prompt': prompt,
                    'stream': False,
                    **kwargs
                },
                timeout=timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'response': data.get('response', ''),
                'model': data.get('model', model_name),
                'provider': 'ollama',
                'success': True,
                'metadata': {
                    'created_at': data.get('created_at'),
                    'total_duration': data.get('total_duration'),
                    'load_duration': data.get('load_duration'),
                    'prompt_eval_count': data.get('prompt_eval_count'),
                    'eval_count': data.get('eval_count')
                }
            }
            
        except requests.exceptions.Timeout:
            logger.error(f'Ollama API timeout after {timeout}s')
            raise APIError('AI service timeout. Please try again.', 504)
        except requests.exceptions.ConnectionError:
            logger.error('Cannot connect to Ollama service')
            raise APIError('AI service unavailable. Please ensure Ollama is running.', 503)
        except requests.exceptions.RequestException as e:
            logger.error(f'Ollama API error: {str(e)}')
            raise APIError(f'AI service error: {str(e)}', 500)
    
    def stream_chat(self, prompt: str, model: Optional[str] = None, **kwargs):
        """
        Stream chat responses from Ollama
        
        Args:
            prompt: The prompt/message to send
            model: Optional model override
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        model_name = model or self.default_model
        timeout = kwargs.get('timeout', self.timeout)
        
        try:
            response = requests.post(
                f'{self.api_url}/api/generate',
                json={
                    'model': model_name,
                    'prompt': prompt,
                    'stream': True,
                    **kwargs
                },
                stream=True,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    yield data.get('response', '')
                    
        except requests.exceptions.RequestException as e:
            logger.error(f'Ollama streaming error: {str(e)}')
            raise APIError(f'AI streaming error: {str(e)}', 500)
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is available
        
        Returns:
            True if available, False otherwise
        """
        try:
            response = requests.get(f'{self.api_url}/api/tags', timeout=5)
            return response.status_code == 200
        except Exception as e:
            return False
            logger.debug(f'Ollama availability check failed: {str(e)}')
    
    def get_models(self) -> list:
        """
        Get list of available Ollama models
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f'{self.api_url}/api/tags', timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.warning(f'Could not fetch Ollama models: {str(e)}')
            logger.warning('Could not fetch Ollama models')
            return [self.default_model]

