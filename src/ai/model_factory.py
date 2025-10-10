"""
Model factory for supporting OpenAI and OpenAI Compatible providers
"""

from typing import Any, Optional

from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI

from src.core.config import Config
from src.core.logger import get_logger

logger = get_logger(__name__)


class ModelFactory:
    """Factory for creating AI model instances based on configuration"""

    @staticmethod
    def create_model(config: Config) -> BaseLanguageModel:
        """
        Create an AI model instance based on the provider configuration
        
        Args:
            config: Application configuration
            
        Returns:
            Configured language model instance
            
        Raises:
            ValueError: If the provider is not supported or configuration is invalid
        """
        provider = config.ai_provider.lower()
        
        if provider == "openai":
            return ModelFactory._create_openai_model(config)
        elif provider == "openai_compatible":
            return ModelFactory._create_openai_compatible_model(config)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    

    @staticmethod
    def _create_openai_model(config: Config) -> ChatOpenAI:
        """Create OpenAI model"""
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        
        logger.info(f"Creating OpenAI model: {config.openai_model}")
        return ChatOpenAI(
            model=config.openai_model,
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            max_tokens=config.openai_max_tokens,
        )

    @staticmethod
    def _create_openai_compatible_model(config: Config) -> ChatOpenAI:
        """Create OpenAI-compatible model (e.g., Ollama, LocalAI)"""
        # Note: OpenAI-compatible endpoints might not require an API key
        api_key = config.openai_compatible_api_key or "not-required"
        
        logger.info(f"Creating OpenAI-compatible model: {config.openai_compatible_model} at {config.openai_compatible_base_url}")
        return ChatOpenAI(
            model=config.openai_compatible_model,
            api_key=api_key,
            base_url=config.openai_compatible_base_url,
            max_tokens=config.openai_compatible_max_tokens,
        )

    @staticmethod
    def get_model_info(config: Config) -> dict[str, Any]:
        """Get information about the current model configuration"""
        provider = config.ai_provider.lower()
        
        if provider == "openai":
            return {
                "provider": "OpenAI",
                "model": config.openai_model,
                "base_url": config.openai_base_url,
                "max_tokens": config.openai_max_tokens,
                "api_configured": bool(config.openai_api_key),
            }
        elif provider == "openai_compatible":
            return {
                "provider": "OpenAI Compatible",
                "model": config.openai_compatible_model,
                "base_url": config.openai_compatible_base_url,
                "max_tokens": config.openai_compatible_max_tokens,
                "api_configured": True,  # OpenAI Compatible endpoints often don't need API keys
            }
        else:
            return {
                "provider": "Unknown",
                "model": "Unknown",
                "api_configured": False,
            }
