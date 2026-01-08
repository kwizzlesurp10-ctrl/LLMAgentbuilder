"""Tests for configuration validation."""
import pytest
from pydantic import ValidationError
from llm_agent_builder.config.models import (
    ServerConfig,
    ProviderConfig,
    ProvidersConfig,
    DatabaseConfig,
    LoggingConfig,
    AppConfig,
)


def test_server_config_validation():
    """Test ServerConfig validation."""
    # Valid config
    config = ServerConfig(host="localhost", port=8080)
    assert config.host == "localhost"
    assert config.port == 8080
    
    # Invalid port (too low)
    with pytest.raises(ValidationError):
        ServerConfig(port=0)
    
    # Invalid port (too high)
    with pytest.raises(ValidationError):
        ServerConfig(port=70000)
    
    # Valid defaults
    config = ServerConfig()
    assert config.host == "0.0.0.0"
    assert config.port == 7860
    assert config.workers == 4


def test_provider_config_validation():
    """Test ProviderConfig validation."""
    # Valid config
    config = ProviderConfig(
        api_key_env="TEST_KEY",
        default_model="test-model",
        rate_limit=10
    )
    assert config.api_key_env == "TEST_KEY"
    assert config.default_model == "test-model"
    assert config.rate_limit == 10
    
    # Missing required fields
    with pytest.raises(ValidationError):
        ProviderConfig()
    
    # Invalid rate limit
    with pytest.raises(ValidationError):
        ProviderConfig(
            api_key_env="TEST_KEY",
            default_model="test-model",
            rate_limit=0
        )


def test_providers_config_defaults():
    """Test ProvidersConfig has correct defaults."""
    config = ProvidersConfig()
    
    # Check google provider defaults
    assert config.google.api_key_env == "GOOGLE_GEMINI_KEY"
    assert config.google.default_model == "gemini-1.5-pro"
    assert config.google.rate_limit == 20
    
    # Check anthropic provider defaults
    assert config.anthropic.api_key_env == "ANTHROPIC_API_KEY"
    assert config.anthropic.default_model == "claude-3-5-sonnet-20241022"
    assert config.anthropic.rate_limit == 20


def test_database_config_validation():
    """Test DatabaseConfig validation."""
    # Valid config
    config = DatabaseConfig(workflow_db="test.db", pool_size=10)
    assert config.workflow_db == "test.db"
    assert config.pool_size == 10
    
    # Invalid pool size
    with pytest.raises(ValidationError):
        DatabaseConfig(pool_size=0)
    
    # Defaults
    config = DatabaseConfig()
    assert config.workflow_db == "workflow.db"
    assert config.pool_size == 5


def test_logging_config_validation():
    """Test LoggingConfig validation."""
    # Valid config
    config = LoggingConfig(level="DEBUG", format="%(message)s")
    assert config.level == "DEBUG"
    assert config.format == "%(message)s"
    
    # Invalid logging level
    with pytest.raises(ValidationError):
        LoggingConfig(level="INVALID")
    
    # Case insensitive level validation
    config = LoggingConfig(level="debug")
    assert config.level == "DEBUG"
    
    config = LoggingConfig(level="info")
    assert config.level == "INFO"
    
    # Defaults
    config = LoggingConfig()
    assert config.level == "INFO"
    assert config.file is None


def test_app_config_validation():
    """Test AppConfig validation."""
    # Valid minimal config
    config = AppConfig()
    assert config.server.port == 7860
    assert config.environment == "production"
    
    # Custom config
    config = AppConfig(
        server=ServerConfig(port=9000),
        environment="development"
    )
    assert config.server.port == 9000
    assert config.environment == "development"
    
    # Invalid environment
    with pytest.raises(ValidationError):
        AppConfig(environment="invalid_env")
    
    # Valid environments
    for env in ["development", "staging", "production", "test"]:
        config = AppConfig(environment=env)
        assert config.environment == env.lower()


def test_app_config_get_provider_config():
    """Test AppConfig.get_provider_config method."""
    config = AppConfig()
    
    # Get google provider
    google = config.get_provider_config("google")
    assert google is not None
    assert google.default_model == "gemini-1.5-pro"
    
    # Get anthropic provider
    anthropic = config.get_provider_config("anthropic")
    assert anthropic is not None
    assert anthropic.default_model == "claude-3-5-sonnet-20241022"
    
    # Get non-existent provider
    result = config.get_provider_config("nonexistent")
    assert result is None


def test_app_config_get_api_key(monkeypatch):
    """Test AppConfig.get_api_key method."""
    config = AppConfig()
    
    # Set environment variable
    monkeypatch.setenv("GOOGLE_GEMINI_KEY", "test-key-123")
    
    # Get API key
    api_key = config.get_api_key("google")
    assert api_key == "test-key-123"
    
    # Get key for provider without env var set
    api_key = config.get_api_key("anthropic")
    assert api_key is None  # Not set in environment
    
    # Get key for non-existent provider
    api_key = config.get_api_key("nonexistent")
    assert api_key is None


def test_app_config_defaults():
    """Test AppConfig default values."""
    config = AppConfig()
    
    assert config.generated_agents_dir == "generated_agents"
    assert config.template_dir is None
    assert config.enable_metrics is True
    assert config.enable_rate_limiting is True


def test_config_from_dict():
    """Test creating config from dictionary."""
    config_dict = {
        "server": {
            "host": "localhost",
            "port": 8080,
            "workers": 2,
        },
        "logging": {
            "level": "DEBUG",
        },
        "environment": "development",
    }
    
    config = AppConfig(**config_dict)
    assert config.server.host == "localhost"
    assert config.server.port == 8080
    assert config.server.workers == 2
    assert config.logging.level == "DEBUG"
    assert config.environment == "development"


def test_nested_validation():
    """Test that nested validation works correctly."""
    # Invalid nested value
    with pytest.raises(ValidationError):
        AppConfig(**{
            "server": {
                "port": -1,  # Invalid
            }
        })
    
    # Invalid nested logging level
    with pytest.raises(ValidationError):
        AppConfig(**{
            "logging": {
                "level": "NOTVALID",
            }
        })
