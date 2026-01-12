"""
Configuration management for LLM Agent Builder.

This module provides centralized configuration management with support for
multiple LLM providers (Google Gemini, Anthropic, OpenAI, HuggingFace).
"""

import os
import warnings
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum


class Provider(Enum):
    """Supported LLM providers."""
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    HUGGINGCHAT = "huggingchat"


@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""
    name: str
    env_var: str
    model_env_var: Optional[str] = None
    default_model: Optional[str] = None
    deprecated_env_vars: Optional[List[str]] = None


# Provider configuration mappings
PROVIDER_CONFIGS: Dict[Provider, ProviderConfig] = {
    Provider.GOOGLE: ProviderConfig(
        name="Google Gemini",
        env_var="GOOGLE_GEMINI_KEY",
        model_env_var="GOOGLE_GEMINI_MODEL",
        default_model="gemini-1.5-pro",
        deprecated_env_vars=None
    ),
    Provider.ANTHROPIC: ProviderConfig(
        name="Anthropic Claude",
        env_var="ANTHROPIC_API_KEY",
        model_env_var="ANTHROPIC_MODEL",
        default_model="claude-3-5-sonnet-20241022",
        deprecated_env_vars=None
    ),
    Provider.OPENAI: ProviderConfig(
        name="OpenAI",
        env_var="OPENAI_API_KEY",
        model_env_var="OPENAI_MODEL",
        default_model="gpt-4",
        deprecated_env_vars=None
    ),
    Provider.HUGGINGFACE: ProviderConfig(
        name="HuggingFace",
        env_var="HUGGINGFACEHUB_API_TOKEN",
        model_env_var="HUGGINGFACE_MODEL",
        default_model="meta-llama/Meta-Llama-3-8B-Instruct",
        deprecated_env_vars=None
    ),
    Provider.HUGGINGCHAT: ProviderConfig(
        name="HuggingChat",
        env_var="HUGGINGFACEHUB_API_TOKEN",
        model_env_var="HUGGINGCHAT_MODEL",
        default_model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        deprecated_env_vars=None
    ),
}


class ConfigManager:
    """
    Centralized configuration manager for LLM Agent Builder.
    
    This singleton class manages API keys and configuration for all supported
    providers, with backward compatibility and deprecation warnings.
    """
    
    _instance: Optional['ConfigManager'] = None
    
    def __new__(cls) -> 'ConfigManager':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the configuration manager."""
        if self._initialized:
            return
        self._initialized = True
        self._api_keys: Dict[Provider, Optional[str]] = {}
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load configuration from environment variables."""
        for provider, config in PROVIDER_CONFIGS.items():
            # Try primary environment variable
            api_key = os.environ.get(config.env_var)
            
            # Check for deprecated environment variables
            if not api_key and config.deprecated_env_vars:
                for deprecated_var in config.deprecated_env_vars:
                    api_key = os.environ.get(deprecated_var)
                    if api_key:
                        warnings.warn(
                            f"Environment variable '{deprecated_var}' is deprecated. "
                            f"Please use '{config.env_var}' instead.",
                            DeprecationWarning,
                            stacklevel=2
                        )
                        break
            
            self._api_keys[provider] = api_key
    
    def get_api_key(self, provider: Provider) -> Optional[str]:
        """
        Get API key for a specific provider.
        
        :param provider: The provider to get the API key for
        :return: API key if available, None otherwise
        """
        return self._api_keys.get(provider)
    
    def get_api_key_by_name(self, provider_name: str) -> Optional[str]:
        """
        Get API key for a provider by name string.
        
        :param provider_name: Provider name (google, anthropic, openai, etc.)
        :return: API key if available, None otherwise
        """
        try:
            provider = Provider(provider_name.lower())
            return self.get_api_key(provider)
        except (ValueError, KeyError):
            return None
    
    def get_any_api_key(self) -> Optional[str]:
        """
        Get any available API key.
        
        Priority order: Google Gemini, HuggingFace, Anthropic, OpenAI
        
        :return: First available API key, None if none available
        """
        priority_order = [
            Provider.GOOGLE,
            Provider.HUGGINGFACE,
            Provider.ANTHROPIC,
            Provider.OPENAI
        ]
        
        for provider in priority_order:
            api_key = self.get_api_key(provider)
            if api_key:
                return api_key
        
        return None
    
    def has_api_key(self, provider: Provider) -> bool:
        """
        Check if an API key is available for a provider.
        
        :param provider: The provider to check
        :return: True if API key is available, False otherwise
        """
        return self.get_api_key(provider) is not None
    
    def validate_provider(self, provider_name: str) -> bool:
        """
        Validate that a provider has a configured API key.
        
        :param provider_name: Provider name to validate
        :return: True if provider has API key, False otherwise
        :raises ValueError: If provider name is not recognized
        """
        try:
            provider = Provider(provider_name.lower())
        except ValueError:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Supported providers: {', '.join([p.value for p in Provider])}"
            )
        
        return self.has_api_key(provider)
    
    def get_model(self, provider: Provider) -> str:
        """
        Get the model name for a provider.
        
        Checks environment variable first, falls back to default.
        
        :param provider: The provider to get the model for
        :return: Model name
        """
        config = PROVIDER_CONFIGS[provider]
        
        if config.model_env_var:
            model = os.environ.get(config.model_env_var)
            if model:
                return model
        
        return config.default_model or ""
    
    def get_provider_config(self, provider: Provider) -> ProviderConfig:
        """
        Get the configuration for a provider.
        
        :param provider: The provider to get configuration for
        :return: Provider configuration
        """
        return PROVIDER_CONFIGS[provider]
    
    def get_configuration_status(self) -> Dict[str, Dict[str, any]]:
        """
        Get the status of all provider configurations.
        
        :return: Dictionary with provider status information
        """
        status = {}
        
        for provider, config in PROVIDER_CONFIGS.items():
            has_key = self.has_api_key(provider)
            status[provider.value] = {
                "name": config.name,
                "env_var": config.env_var,
                "configured": has_key,
                "model": self.get_model(provider) if has_key else None
            }
        
        return status
    
    def validate_configuration(
        self,
        require_any: bool = True,
        required_providers: Optional[List[Provider]] = None
    ) -> tuple[bool, List[str]]:
        """
        Validate that required API keys are configured.
        
        :param require_any: If True, at least one API key must be configured
        :param required_providers: List of providers that must have API keys
        :return: Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check required providers
        if required_providers:
            for provider in required_providers:
                if not self.has_api_key(provider):
                    config = PROVIDER_CONFIGS[provider]
                    errors.append(
                        f"Missing API key for {config.name}. "
                        f"Please set {config.env_var} environment variable."
                    )
        
        # Check if at least one key is available
        if require_any and not required_providers:
            if not self.get_any_api_key():
                env_vars = [c.env_var for c in PROVIDER_CONFIGS.values()]
                errors.append(
                    f"No API keys found. Please set at least one of: {', '.join(env_vars)}"
                )
        
        return (len(errors) == 0, errors)


# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    Get the singleton ConfigManager instance.
    
    :return: ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_api_key(provider: Provider) -> Optional[str]:
    """
    Convenience function to get an API key for a provider.
    
    :param provider: The provider to get the API key for
    :return: API key if available, None otherwise
    """
    return get_config_manager().get_api_key(provider)


def validate_configuration() -> tuple[bool, List[str]]:
    """
    Convenience function to validate configuration.
    
    :return: Tuple of (is_valid, list of error messages)
    """
    return get_config_manager().validate_configuration()
