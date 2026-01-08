"""Provider registry and implementations."""
from .base import LLMProvider, ProviderRegistry, register_provider

# Auto-import all provider implementations to trigger registration
from .google import GoogleGeminiProvider
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .huggingface import HuggingFaceProvider
from .huggingchat import HuggingChatProvider


def get_provider(name: str) -> LLMProvider:
    """Helper function to get a provider instance by name."""
    return ProviderRegistry.get(name)


__all__ = [
    'LLMProvider',
    'ProviderRegistry',
    'register_provider',
    'get_provider',
    'GoogleGeminiProvider',
    'AnthropicProvider',
    'OpenAIProvider',
    'HuggingFaceProvider',
    'HuggingChatProvider',
]
