"""
AI Service
Unified interface for all AI interactions
"""
import logging
import hashlib
import time
from typing import Dict, Any, Optional
from flask import current_app
from .ai_providers.ollama import OllamaProvider
from .ai_providers.lmstudio import LMStudioProvider
from .prompts import PromptTemplates
from src.utils.errors import APIError

logger = logging.getLogger(__name__)


class AICache:
    """Simple in-memory cache for AI responses"""
    
    def __init__(self, ttl=3600):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.cache = {}
        self.ttl = ttl
    
    def _generate_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model"""
        content = f'{model}:{prompt}'
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response
        
        Args:
            prompt: The prompt
            model: The model name
            
        Returns:
            Cached response or None
        """
        key = self._generate_key(prompt, model)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                logger.info(f'Cache hit for key: {key[:8]}...')
                return entry['response']
            else:
                # Expired
                del self.cache[key]
        return None
    
    def set(self, prompt: str, model: str, response: Dict[str, Any]):
        """
        Cache a response
        
        Args:
            prompt: The prompt
            model: The model name
            response: The response to cache
        """
        key = self._generate_key(prompt, model)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.info(f'Cached response for key: {key[:8]}...')
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()
        logger.info('Cache cleared')
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'ttl': self.ttl
        }


class AIService:
    """Unified AI service for all AI interactions"""
    
    def __init__(self, provider='ollama', enable_cache=True):
        """
        Initialize AI service
        
        Args:
            provider: AI provider name ('ollama', 'openai', etc.)
            enable_cache: Whether to enable response caching
        """
        self.provider_name = provider
        self.enable_cache = enable_cache
        self.cache = AICache() if enable_cache else None
        self.provider = self._initialize_provider(provider)
        self.prompts = PromptTemplates
    
    def _initialize_provider(self, provider_name: str):
        """Initialize the AI provider"""
        if provider_name == 'ollama':
            config = {
                'api_url': current_app.config.get('AI_API_URL', 'http://localhost:11434'),
                'default_model': current_app.config.get('AI_MODEL', 'phi3'),
                'timeout': current_app.config.get('AI_TIMEOUT', 30)
            }
            return OllamaProvider(config)
        elif provider_name == 'lmstudio':
            config = {
                'api_url': current_app.config.get('AI_API_URL', 'http://localhost:1234/v1'),
                'default_model': current_app.config.get('AI_MODEL', 'local-model'),
                'timeout': current_app.config.get('AI_TIMEOUT', 60),
                'temperature': current_app.config.get('AI_TEMPERATURE', 0.7),
                'max_tokens': current_app.config.get('AI_MAX_TOKENS', 2048)
            }
            return LMStudioProvider(config)
        else:
            raise ValueError(f'Unknown AI provider: {provider_name}')
    
    def chat(self, prompt: str, model: Optional[str] = None, use_cache: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Send a chat message to AI
        
        Args:
            prompt: The prompt/message
            model: Optional model override
            use_cache: Whether to use cached responses
            **kwargs: Additional parameters
            
        Returns:
            AI response dict
        """
        model_name = model or self.provider.default_model
        
        # Check cache
        if self.enable_cache and use_cache:
            cached = self.cache.get(prompt, model_name)
            if cached:
                return cached
        
        # Call provider
        response = self.provider.chat(prompt, model, **kwargs)
        
        # Cache response
        if self.enable_cache and use_cache:
            self.cache.set(prompt, model_name, response)
        
        return response
    
    def execute_agent(self, agent_name: str, context: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specialized AI agent
        
        Args:
            agent_name: Name of the agent
            context: Context for the agent
            **kwargs: Additional parameters
            
        Returns:
            AI response dict
        """
        try:
            prompt = self.prompts.get_agent_prompt(agent_name, context)
            response = self.chat(prompt, timeout=60, **kwargs)
            response['agent'] = agent_name
            return response
        except ValueError as e:
            raise APIError(str(e), 404)
    
    def summarize(self, content: str, **kwargs) -> Dict[str, Any]:
        """
        Summarize content
        
        Args:
            content: Content to summarize
            **kwargs: Additional parameters
            
        Returns:
            AI response dict with summary
        """
        if not content or len(content) < 10:
            raise APIError('Content is required and must be at least 10 characters', 400)
        
        if len(content) > 50000:
            raise APIError('Content is too long (max 50,000 characters)', 400)
        
        prompt = self.prompts.get_task_prompt('summarize', content=content)
        return self.chat(prompt, timeout=45, **kwargs)
    
    def analyze(self, content: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze content
        
        Args:
            content: Content to analyze
            **kwargs: Additional parameters
            
        Returns:
            AI response dict with analysis
        """
        prompt = self.prompts.get_task_prompt('analyze', content=content)
        return self.chat(prompt, **kwargs)
    
    def suggest_next_steps(self, task_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Suggest next steps for a task
        
        Args:
            task_data: Task information dict
            **kwargs: Additional parameters
            
        Returns:
            AI response dict with suggestions
        """
        prompt = self.prompts.get_task_prompt(
            'suggest_next_steps',
            title=task_data.get('title', ''),
            description=task_data.get('description', ''),
            status=task_data.get('status', '')
        )
        return self.chat(prompt, **kwargs)
    
    def chat_with_context(self, question: str, task_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Chat with task context
        
        Args:
            question: User question
            task_data: Task information dict
            **kwargs: Additional parameters
            
        Returns:
            AI response dict
        """
        prompt = self.prompts.get_chat_prompt(
            'task_context',
            title=task_data.get('title', ''),
            description=task_data.get('description', ''),
            status=task_data.get('status', ''),
            priority=task_data.get('priority', ''),
            question=question
        )
        return self.chat(prompt, use_cache=False, **kwargs)
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.provider.is_available()
    
    def get_available_agents(self) -> list:
        """Get list of available agents"""
        return self.prompts.list_agents()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.cache:
            return self.cache.stats()
        return {'enabled': False}
    
    def clear_cache(self):
        """Clear the cache"""
        if self.cache:
            self.cache.clear()


# Global AI service instance
_ai_service = None


def get_ai_service() -> AIService:
    """
    Get or create the global AI service instance
    
    Returns:
        AIService instance
    """
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

