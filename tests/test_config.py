"""
Tests for configuration management module.
"""

import pytest
import os
import warnings
from llm_agent_builder.config import (
    ConfigManager,
    Provider,
    ProviderConfig,
    PROVIDER_CONFIGS,
    get_config_manager,
    get_api_key,
    validate_configuration
)


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment fixture - removes all API keys."""
    # Remove all provider API keys
    monkeypatch.delenv("GOOGLE_GEMINI_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HUGGINGFACEHUB_API_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_COPILOT_TOKEN", raising=False)
    
    # Reset singleton instance to force reload
    ConfigManager._instance = None


@pytest.fixture
def mock_google_env(monkeypatch):
    """Mock environment with Google Gemini key."""
    monkeypatch.setenv("GOOGLE_GEMINI_KEY", "test-google-key")
    monkeypatch.setenv("GOOGLE_GEMINI_MODEL", "gemini-1.5-pro")
    # Reset singleton instance to force reload
    ConfigManager._instance = None


@pytest.fixture
def mock_anthropic_env(monkeypatch):
    """Mock environment with Anthropic key."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    # Reset singleton instance to force reload
    ConfigManager._instance = None


@pytest.fixture
def mock_multi_provider_env(monkeypatch):
    """Mock environment with multiple provider keys."""
    monkeypatch.setenv("GOOGLE_GEMINI_KEY", "test-google-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HUGGINGFACEHUB_API_TOKEN", "test-hf-token")
    # Reset singleton instance to force reload
    ConfigManager._instance = None


class TestProviderConfig:
    """Tests for ProviderConfig dataclass."""
    
    def test_provider_config_structure(self):
        """Test that all providers have proper configuration."""
        assert len(PROVIDER_CONFIGS) == 5
        
        # Check Google config
        google_config = PROVIDER_CONFIGS[Provider.GOOGLE]
        assert google_config.name == "Google Gemini"
        assert google_config.env_var == "GOOGLE_GEMINI_KEY"
        assert google_config.model_env_var == "GOOGLE_GEMINI_MODEL"
        assert google_config.default_model == "gemini-1.5-pro"
        
        # Check Anthropic config
        anthropic_config = PROVIDER_CONFIGS[Provider.ANTHROPIC]
        assert anthropic_config.name == "Anthropic Claude"
        assert anthropic_config.env_var == "ANTHROPIC_API_KEY"
        assert anthropic_config.model_env_var == "ANTHROPIC_MODEL"
        
        # Check HuggingFace config
        hf_config = PROVIDER_CONFIGS[Provider.HUGGINGFACE]
        assert hf_config.name == "HuggingFace"
        assert hf_config.env_var == "HUGGINGFACEHUB_API_TOKEN"


class TestConfigManager:
    """Tests for ConfigManager class."""
    
    def test_singleton_pattern(self, mock_google_env):
        """Test that ConfigManager implements singleton pattern."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        assert manager1 is manager2
    
    def test_get_api_key_google(self, mock_google_env):
        """Test getting Google API key."""
        config_manager = ConfigManager()
        api_key = config_manager.get_api_key(Provider.GOOGLE)
        assert api_key == "test-google-key"
    
    def test_get_api_key_anthropic(self, mock_anthropic_env):
        """Test getting Anthropic API key."""
        config_manager = ConfigManager()
        api_key = config_manager.get_api_key(Provider.ANTHROPIC)
        assert api_key == "test-anthropic-key"
    
    def test_get_api_key_by_name(self, mock_google_env):
        """Test getting API key by provider name string."""
        config_manager = ConfigManager()
        api_key = config_manager.get_api_key_by_name("google")
        assert api_key == "test-google-key"
    
    def test_get_api_key_by_name_invalid(self, mock_google_env):
        """Test getting API key with invalid provider name."""
        config_manager = ConfigManager()
        api_key = config_manager.get_api_key_by_name("invalid")
        assert api_key is None
    
    def test_get_any_api_key_priority(self, mock_multi_provider_env):
        """Test that get_any_api_key follows priority order."""
        config_manager = ConfigManager()
        # Should return Google key first (highest priority)
        api_key = config_manager.get_any_api_key()
        assert api_key == "test-google-key"
    
    def test_get_any_api_key_no_keys(self, clean_env):
        """Test get_any_api_key when no keys are configured."""
        config_manager = ConfigManager()
        api_key = config_manager.get_any_api_key()
        assert api_key is None
    
    def test_has_api_key(self, mock_google_env):
        """Test checking if provider has API key."""
        config_manager = ConfigManager()
        assert config_manager.has_api_key(Provider.GOOGLE) is True
        assert config_manager.has_api_key(Provider.ANTHROPIC) is False
    
    def test_validate_provider_valid(self, mock_google_env):
        """Test validating a provider with configured key."""
        config_manager = ConfigManager()
        assert config_manager.validate_provider("google") is True
    
    def test_validate_provider_invalid_name(self, mock_google_env):
        """Test validating a provider with invalid name."""
        config_manager = ConfigManager()
        with pytest.raises(ValueError, match="Unknown provider"):
            config_manager.validate_provider("invalid")
    
    def test_validate_provider_not_configured(self, mock_google_env):
        """Test validating a provider without configured key."""
        config_manager = ConfigManager()
        assert config_manager.validate_provider("anthropic") is False
    
    def test_get_model_from_env(self, mock_google_env):
        """Test getting model from environment variable."""
        config_manager = ConfigManager()
        model = config_manager.get_model(Provider.GOOGLE)
        assert model == "gemini-1.5-pro"
    
    def test_get_model_default(self, clean_env):
        """Test getting default model when env var not set."""
        config_manager = ConfigManager()
        model = config_manager.get_model(Provider.GOOGLE)
        assert model == "gemini-1.5-pro"
    
    def test_get_provider_config(self, clean_env):
        """Test getting provider configuration."""
        config_manager = ConfigManager()
        config = config_manager.get_provider_config(Provider.GOOGLE)
        assert isinstance(config, ProviderConfig)
        assert config.name == "Google Gemini"
    
    def test_get_configuration_status(self, mock_google_env):
        """Test getting configuration status for all providers."""
        config_manager = ConfigManager()
        status = config_manager.get_configuration_status()
        
        assert len(status) == 5
        assert status["google"]["configured"] is True
        assert status["anthropic"]["configured"] is False
        assert status["google"]["model"] == "gemini-1.5-pro"
    
    def test_validate_configuration_success(self, mock_google_env):
        """Test configuration validation when at least one key is set."""
        config_manager = ConfigManager()
        is_valid, errors = config_manager.validate_configuration()
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_configuration_failure(self, clean_env):
        """Test configuration validation when no keys are set."""
        config_manager = ConfigManager()
        is_valid, errors = config_manager.validate_configuration()
        assert is_valid is False
        assert len(errors) > 0
        assert "No API keys found" in errors[0]
    
    def test_validate_configuration_required_providers(self, mock_google_env):
        """Test configuration validation with required providers."""
        config_manager = ConfigManager()
        is_valid, errors = config_manager.validate_configuration(
            require_any=False,
            required_providers=[Provider.ANTHROPIC]
        )
        assert is_valid is False
        assert len(errors) > 0
        assert "Anthropic Claude" in errors[0]


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_get_config_manager(self, mock_google_env):
        """Test get_config_manager convenience function."""
        manager = get_config_manager()
        assert isinstance(manager, ConfigManager)
    
    def test_get_api_key_convenience(self, mock_google_env):
        """Test get_api_key convenience function."""
        api_key = get_api_key(Provider.GOOGLE)
        assert api_key == "test-google-key"
    
    def test_validate_configuration_convenience(self, mock_google_env):
        """Test validate_configuration convenience function."""
        is_valid, errors = validate_configuration()
        assert is_valid is True
        assert len(errors) == 0


class TestBackwardCompatibility:
    """Tests for backward compatibility features."""
    
    def test_google_gemini_key_works(self, monkeypatch):
        """Test that GOOGLE_GEMINI_KEY still works."""
        monkeypatch.setenv("GOOGLE_GEMINI_KEY", "test-key")
        ConfigManager._instance = None
        
        config_manager = ConfigManager()
        api_key = config_manager.get_api_key(Provider.GOOGLE)
        assert api_key == "test-key"
    
    def test_huggingface_token_works(self, monkeypatch):
        """Test that HUGGINGFACEHUB_API_TOKEN still works."""
        monkeypatch.setenv("HUGGINGFACEHUB_API_TOKEN", "test-hf-token")
        ConfigManager._instance = None
        
        config_manager = ConfigManager()
        api_key = config_manager.get_api_key(Provider.HUGGINGFACE)
        assert api_key == "test-hf-token"
