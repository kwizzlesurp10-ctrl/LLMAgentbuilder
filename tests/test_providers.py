"""Tests for provider registry and base functionality."""
import pytest
from llm_agent_builder.providers import (
    ProviderRegistry,
    LLMProvider,
    register_provider,
    get_provider
)


def test_provider_registry_contains_all_providers():
    """Test that all expected providers are registered."""
    expected_providers = ['google', 'anthropic', 'openai', 'huggingface', 'huggingchat']
    registered = ProviderRegistry.get_all_names()
    
    for provider in expected_providers:
        assert provider in registered, f"Provider {provider} not registered"


def test_provider_registry_get_valid_provider():
    """Test getting a valid provider from the registry."""
    provider = ProviderRegistry.get('google')
    assert provider is not None
    assert isinstance(provider, LLMProvider)


def test_provider_registry_get_invalid_provider():
    """Test that getting an invalid provider raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        ProviderRegistry.get('nonexistent')
    
    assert "not found in registry" in str(exc_info.value)
    assert "Available providers" in str(exc_info.value)


def test_provider_registry_is_registered():
    """Test checking if a provider is registered."""
    assert ProviderRegistry.is_registered('google')
    assert ProviderRegistry.is_registered('anthropic')
    assert not ProviderRegistry.is_registered('nonexistent')


def test_provider_registry_case_insensitive():
    """Test that provider lookup is case-insensitive."""
    provider_lower = ProviderRegistry.get('google')
    provider_upper = ProviderRegistry.get('GOOGLE')
    provider_mixed = ProviderRegistry.get('Google')
    
    # All should return instances of the same class
    assert type(provider_lower) == type(provider_upper) == type(provider_mixed)


def test_get_provider_helper():
    """Test the get_provider helper function."""
    provider = get_provider('openai')
    assert provider is not None
    assert isinstance(provider, LLMProvider)


def test_register_provider_decorator():
    """Test the register_provider decorator."""
    @register_provider("test_provider")
    class TestProvider(LLMProvider):
        def get_template_name(self) -> str:
            return "test_template.py.j2"
        
        def validate_config(self, config: dict) -> bool:
            return True
        
        def get_env_var_name(self) -> str:
            return "TEST_API_KEY"
        
        def get_default_model(self) -> str:
            return "test-model"
        
        def get_supported_models(self) -> list:
            return ["test-model"]
    
    # Verify it was registered
    assert ProviderRegistry.is_registered("test_provider")
    
    # Verify we can get it
    provider = ProviderRegistry.get("test_provider")
    assert isinstance(provider, TestProvider)
    assert provider.get_template_name() == "test_template.py.j2"
    
    # Clean up using unregister method
    ProviderRegistry.unregister("test_provider")


def test_provider_interface_methods():
    """Test that all providers implement the required interface."""
    providers = ProviderRegistry.get_all_names()
    
    for provider_name in providers:
        provider = ProviderRegistry.get(provider_name)
        
        # Test all required methods exist and return expected types
        assert isinstance(provider.get_template_name(), str)
        assert isinstance(provider.get_env_var_name(), str)
        assert isinstance(provider.get_default_model(), str)
        assert isinstance(provider.get_supported_models(), list)
        assert len(provider.get_supported_models()) > 0
        
        # Test validate_config accepts a dict
        result = provider.validate_config({"model": provider.get_default_model()})
        assert isinstance(result, bool)


def test_provider_returns_valid_template_names():
    """Test that all providers return valid template names."""
    providers = ProviderRegistry.get_all_names()
    
    for provider_name in providers:
        provider = ProviderRegistry.get(provider_name)
        template_name = provider.get_template_name()
        
        # Template name should end with .j2
        assert template_name.endswith('.j2'), f"{provider_name} template should end with .j2"
        
        # Template name should start with agent_template
        assert template_name.startswith('agent_template'), \
            f"{provider_name} template should start with agent_template"


def test_provider_supported_models_not_empty():
    """Test that all providers have non-empty supported models list."""
    providers = ProviderRegistry.get_all_names()

    for provider_name in providers:
        provider = ProviderRegistry.get(provider_name)
        models = provider.get_supported_models()

        assert len(models) > 0, f"{provider_name} should have at least one supported model"

        # Verify default model is in supported models
        default_model = provider.get_default_model()
        assert default_model in models, \
            f"{provider_name} default model should be in supported models"