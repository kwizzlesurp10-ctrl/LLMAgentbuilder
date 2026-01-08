"""Tests for individual provider implementations."""
import pytest
from llm_agent_builder.providers import (
    GoogleGeminiProvider,
    AnthropicProvider,
    OpenAIProvider,
    HuggingFaceProvider,
    HuggingChatProvider,
    ProviderRegistry
)


class TestGoogleGeminiProvider:
    """Tests for Google Gemini provider."""
    
    def test_template_name(self):
        provider = GoogleGeminiProvider()
        assert provider.get_template_name() == "agent_template.py.j2"
    
    def test_env_var_name(self):
        provider = GoogleGeminiProvider()
        assert provider.get_env_var_name() == "GOOGLE_GEMINI_KEY"
    
    def test_default_model(self):
        provider = GoogleGeminiProvider()
        assert provider.get_default_model() == "gemini-1.5-pro"
    
    def test_supported_models(self):
        provider = GoogleGeminiProvider()
        models = provider.get_supported_models()
        assert "gemini-1.5-pro" in models
        assert "gemini-1.5-flash" in models
        assert len(models) >= 2
    
    def test_validate_config_valid_model(self):
        provider = GoogleGeminiProvider()
        config = {"model": "gemini-1.5-pro"}
        assert provider.validate_config(config) is True
    
    def test_validate_config_invalid_model(self):
        provider = GoogleGeminiProvider()
        config = {"model": "invalid-model"}
        assert provider.validate_config(config) is False
    
    def test_validate_config_no_model(self):
        provider = GoogleGeminiProvider()
        config = {}
        assert provider.validate_config(config) is True


class TestAnthropicProvider:
    """Tests for Anthropic provider."""
    
    def test_template_name(self):
        provider = AnthropicProvider()
        assert provider.get_template_name() == "agent_template.py.j2"
    
    def test_env_var_name(self):
        provider = AnthropicProvider()
        assert provider.get_env_var_name() == "ANTHROPIC_API_KEY"
    
    def test_default_model(self):
        provider = AnthropicProvider()
        assert provider.get_default_model() == "claude-3-5-sonnet-20241022"
    
    def test_supported_models(self):
        provider = AnthropicProvider()
        models = provider.get_supported_models()
        assert "claude-3-5-sonnet-20241022" in models
        assert len(models) >= 2
    
    def test_validate_config_valid_model(self):
        provider = AnthropicProvider()
        config = {"model": "claude-3-5-sonnet-20241022"}
        assert provider.validate_config(config) is True


class TestOpenAIProvider:
    """Tests for OpenAI provider."""
    
    def test_template_name(self):
        provider = OpenAIProvider()
        assert provider.get_template_name() == "agent_template_openai.py.j2"
    
    def test_env_var_name(self):
        provider = OpenAIProvider()
        assert provider.get_env_var_name() == "OPENAI_API_KEY"
    
    def test_default_model(self):
        provider = OpenAIProvider()
        assert provider.get_default_model() == "gpt-4o"
    
    def test_supported_models(self):
        provider = OpenAIProvider()
        models = provider.get_supported_models()
        assert "gpt-4o" in models
        assert "gpt-4" in models
        assert len(models) >= 3
    
    def test_validate_config_valid_model(self):
        provider = OpenAIProvider()
        config = {"model": "gpt-4o"}
        assert provider.validate_config(config) is True


class TestHuggingFaceProvider:
    """Tests for HuggingFace provider."""
    
    def test_template_name(self):
        provider = HuggingFaceProvider()
        assert provider.get_template_name() == "agent_template_hf.py.j2"
    
    def test_env_var_name(self):
        provider = HuggingFaceProvider()
        assert provider.get_env_var_name() == "HUGGINGFACEHUB_API_TOKEN"
    
    def test_default_model(self):
        provider = HuggingFaceProvider()
        assert provider.get_default_model() == "meta-llama/Meta-Llama-3-8B-Instruct"
    
    def test_supported_models(self):
        provider = HuggingFaceProvider()
        models = provider.get_supported_models()
        assert "meta-llama/Meta-Llama-3-8B-Instruct" in models
        assert len(models) >= 1
    
    def test_validate_config_valid_model(self):
        provider = HuggingFaceProvider()
        config = {"model": "meta-llama/Meta-Llama-3-8B-Instruct"}
        assert provider.validate_config(config) is True


class TestHuggingChatProvider:
    """Tests for HuggingChat provider."""
    
    def test_template_name(self):
        provider = HuggingChatProvider()
        assert provider.get_template_name() == "agent_template_huggingchat.py.j2"
    
    def test_env_var_name(self):
        provider = HuggingChatProvider()
        assert provider.get_env_var_name() == "HUGGINGCHAT_EMAIL"
    
    def test_default_model(self):
        provider = HuggingChatProvider()
        assert provider.get_default_model() == "meta-llama/Meta-Llama-3.1-70B-Instruct"
    
    def test_supported_models(self):
        provider = HuggingChatProvider()
        models = provider.get_supported_models()
        assert "meta-llama/Meta-Llama-3.1-70B-Instruct" in models
        assert len(models) >= 3
    
    def test_validate_config_valid_model(self):
        provider = HuggingChatProvider()
        config = {"model": "meta-llama/Meta-Llama-3.1-70B-Instruct"}
        assert provider.validate_config(config) is True


class TestProviderIntegration:
    """Integration tests for providers with AgentBuilder."""
    
    def test_all_providers_can_be_retrieved(self):
        """Test that all providers can be retrieved and instantiated."""
        provider_names = ['google', 'anthropic', 'openai', 'huggingface', 'huggingchat']
        
        for name in provider_names:
            provider = ProviderRegistry.get(name)
            assert provider is not None
            assert hasattr(provider, 'get_template_name')
    
    def test_provider_template_consistency(self):
        """Test that provider templates match their implementation."""
        # Google and Anthropic should use the same base template
        google = GoogleGeminiProvider()
        anthropic = AnthropicProvider()
        assert google.get_template_name() == anthropic.get_template_name()
        
        # OpenAI should have its own template
        openai = OpenAIProvider()
        assert openai.get_template_name() == "agent_template_openai.py.j2"
        
        # HuggingFace should have its own template
        hf = HuggingFaceProvider()
        assert hf.get_template_name() == "agent_template_hf.py.j2"
        
        # HuggingChat should have its own template
        hc = HuggingChatProvider()
        assert hc.get_template_name() == "agent_template_huggingchat.py.j2"
    
    def test_model_validation_across_providers(self):
        """Test that model validation works correctly for all providers."""
        test_cases = [
            ('google', 'gemini-1.5-pro', True),
            ('google', 'invalid-model', False),
            ('anthropic', 'claude-3-5-sonnet-20241022', True),
            ('anthropic', 'invalid-model', False),
            ('openai', 'gpt-4o', True),
            ('openai', 'invalid-model', False),
            ('huggingface', 'meta-llama/Meta-Llama-3-8B-Instruct', True),
            ('huggingface', 'invalid-model', False),
            ('huggingchat', 'meta-llama/Meta-Llama-3.1-70B-Instruct', True),
            ('huggingchat', 'invalid-model', False),
        ]
        
        for provider_name, model, expected_valid in test_cases:
            provider = ProviderRegistry.get(provider_name)
            config = {"model": model}
            result = provider.validate_config(config)
            assert result == expected_valid, \
                f"{provider_name} validation failed for model {model}"
