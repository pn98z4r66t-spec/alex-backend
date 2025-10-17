"""
LM Studio AI Provider
Implementation for LM Studio local AI service with OpenAI-compatible API
"""
import requests
import logging
from typing import Dict, Any, Optional, List
from .base import AIProvider
from src.utils.errors import APIError

logger = logging.getLogger(__name__)


class LMStudioProvider(AIProvider):
    """
    LM Studio AI provider implementation
    
    LM Studio provides an OpenAI-compatible API endpoint, making it easy to
    integrate with existing OpenAI client code. Default port is 1234.
    
    Features:
    - OpenAI-compatible API
    - Easy model switching via UI
    - Better performance than Ollama on some systems
    - User-friendly interface
    - Supports chat completions and embeddings
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LM Studio provider
        
        Args:
            config: Configuration dict with 'api_url' and 'default_model'
                   api_url: LM Studio server URL (default: http://localhost:1234/v1)
                   default_model: Model name (can be any loaded in LM Studio)
        """
        super().__init__(config)
        self.api_url = config.get('api_url', 'http://localhost:1234/v1')
        self.default_model = config.get('default_model', 'local-model')
        self.timeout = config.get('timeout', 60)
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2048)
    
    def chat(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat message to LM Studio using OpenAI-compatible API
        
        Args:
            prompt: The prompt/message to send
            model: Optional model override (use model loaded in LM Studio)
            **kwargs: Additional parameters:
                - temperature: Sampling temperature (0.0 to 2.0)
                - max_tokens: Maximum tokens to generate
                - top_p: Nucleus sampling parameter
                - frequency_penalty: Frequency penalty
                - presence_penalty: Presence penalty
                - stop: Stop sequences
                
        Returns:
            Dict containing response and metadata:
                {
                    'response': str,
                    'model': str,
                    'tokens_used': int,
                    'finish_reason': str
                }
                
        Raises:
            APIError: If the request fails
        """
        model_name = model or self.default_model
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        timeout = kwargs.get('timeout', self.timeout)
        
        # Build messages array for chat completion
        messages = [{"role": "user", "content": prompt}]
        
        # Add system message if provided
        if 'system_message' in kwargs:
            messages.insert(0, {"role": "system", "content": kwargs['system_message']})
        
        # Add conversation history if provided
        if 'history' in kwargs:
            # History should be list of {role, content} dicts
            messages = kwargs['history'] + messages
        
        try:
            response = requests.post(
                f'{self.api_url}/chat/completions',
                json={
                    'model': model_name,
                    'messages': messages,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'top_p': kwargs.get('top_p', 1.0),
                    'frequency_penalty': kwargs.get('frequency_penalty', 0.0),
                    'presence_penalty': kwargs.get('presence_penalty', 0.0),
                    'stop': kwargs.get('stop', None),
                    'stream': False
                },
                timeout=timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract response from OpenAI format
            choice = data['choices'][0]
            message = choice['message']
            
            return {
                'response': message['content'],
                'model': data.get('model', model_name),
                'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                'prompt_tokens': data.get('usage', {}).get('prompt_tokens', 0),
                'completion_tokens': data.get('usage', {}).get('completion_tokens', 0),
                'finish_reason': choice.get('finish_reason', 'stop'),
                'provider': 'lmstudio'
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"LM Studio request timeout after {timeout}s")
            raise APIError(
                f"LM Studio request timeout. Model may be processing. Try increasing timeout.",
                status_code=504
            )
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to LM Studio at {self.api_url}")
            raise APIError(
                f"Cannot connect to LM Studio. Ensure LM Studio is running and a model is loaded.",
                status_code=503
            )
        except requests.exceptions.HTTPError as e:
            logger.error(f"LM Studio HTTP error: {e}")
            error_detail = e.response.json() if e.response.content else str(e)
            raise APIError(
                f"LM Studio error: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            logger.error(f"Unexpected error calling LM Studio: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}", status_code=500)
    
    def stream_chat(self, prompt: str, model: Optional[str] = None, **kwargs):
        """
        Stream chat responses from LM Studio (generator)
        
        Args:
            prompt: The prompt/message to send
            model: Optional model override
            **kwargs: Additional parameters (same as chat())
            
        Yields:
            Chunks of the response as they arrive
            
        Raises:
            APIError: If the request fails
        """
        model_name = model or self.default_model
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        timeout = kwargs.get('timeout', self.timeout)
        
        messages = [{"role": "user", "content": prompt}]
        
        if 'system_message' in kwargs:
            messages.insert(0, {"role": "system", "content": kwargs['system_message']})
        
        if 'history' in kwargs:
            messages = kwargs['history'] + messages
        
        try:
            response = requests.post(
                f'{self.api_url}/chat/completions',
                json={
                    'model': model_name,
                    'messages': messages,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'stream': True
                },
                timeout=timeout,
                stream=True
            )
            
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            delta = data['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Error streaming from LM Studio: {str(e)}")
            raise APIError(f"Streaming error: {str(e)}", status_code=500)
    
    def get_embeddings(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Get embeddings for text using LM Studio
        
        Args:
            text: Text to get embeddings for
            model: Optional model override (must be an embedding model)
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            APIError: If the request fails
        """
        model_name = model or self.default_model
        
        try:
            response = requests.post(
                f'{self.api_url}/embeddings',
                json={
                    'model': model_name,
                    'input': text
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data['data'][0]['embedding']
            
        except Exception as e:
            logger.error(f"Error getting embeddings from LM Studio: {str(e)}")
            raise APIError(f"Embeddings error: {str(e)}", status_code=500)
    
    def is_available(self) -> bool:
        """
        Check if LM Studio is available and has a model loaded
        
        Returns:
            True if LM Studio is running and ready, False otherwise
        """
        try:
            response = requests.get(
                f'{self.api_url}/models',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                # Check if any models are loaded
                models = data.get('data', [])
                return len(models) > 0
            return False
        except Exception as e:
            logger.debug(f"LM Studio not available: {str(e)}")
            return False
    
    def get_models(self) -> List[str]:
        """
        Get list of models currently loaded in LM Studio (required by base class)
        
        Returns:
            List of model names
        """
        return self.get_available_models()
    
    def get_available_models(self) -> List[str]:
        """
        Get list of models currently loaded in LM Studio
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(
                f'{self.api_url}/models',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return [model['id'] for model in data.get('data', [])]
            return []
        except Exception as e:
            logger.error(f"Error getting models from LM Studio: {str(e)}")
            return []
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get provider information
        
        Returns:
            Dict with provider details
        """
        return {
            'name': 'LM Studio',
            'type': 'local',
            'api_url': self.api_url,
            'default_model': self.default_model,
            'available': self.is_available(),
            'loaded_models': self.get_available_models(),
            'features': [
                'chat_completion',
                'streaming',
                'embeddings',
                'openai_compatible'
            ],
            'description': 'LM Studio provides an easy-to-use interface for running local LLMs with OpenAI-compatible API'
        }

