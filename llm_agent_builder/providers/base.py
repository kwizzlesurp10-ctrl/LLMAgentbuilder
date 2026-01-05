"""Base provider classes and registry for LLM providers."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def get_template_name(self) -> str:
        """Return the Jinja2 template filename for this provider."""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict) -> bool:
        """Validate provider-specific configuration."""
        pass
    
    @abstractmethod
    def get_env_var_name(self) -> str:
        """Return the environment variable name for the API key."""
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Return the default model for this provider."""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Return list of supported models for this provider."""
        pass


class ProviderRegistry:
    """Registry for managing LLM provider implementations."""
    
    _providers: Dict[str, Type[LLMProvider]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[LLMProvider]) -> None:
        """Register a provider with a given name."""
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get(cls, name: str) -> LLMProvider:
        """Get a provider instance by name."""
        provider_class = cls._providers.get(name.lower())
        if not provider_class:
            raise ValueError(f"Provider '{name}' not found in registry. "
                           f"Available providers: {', '.join(cls._providers.keys())}")
        return provider_class()
    
    @classmethod
    def get_all_names(cls) -> List[str]:
        """Get all registered provider names."""
        return list(cls._providers.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a provider is registered."""
        return name.lower() in cls._providers


def register_provider(name: str):
    """Decorator to register a provider class."""
    def decorator(cls: Type[LLMProvider]) -> Type[LLMProvider]:
        ProviderRegistry.register(name, cls)
        return cls
    return decorator
