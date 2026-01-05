"""Tests for configuration overrides and priority."""
import pytest
import os
import tempfile
from pathlib import Path
import yaml
from llm_agent_builder.config import (
    get_config_manager,
    reload_config,
)


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables before each test."""
    for key in list(os.environ.keys()):
        if "__" in key or key in ["CONFIG_FILE", "ENVIRONMENT", "ENV"]:
            monkeypatch.delenv(key, raising=False)


@pytest.fixture
def base_config_file(tmp_path):
    """Create a base configuration file."""
    config_file = tmp_path / "base.yaml"
    config_data = {
        "server": {
            "host": "0.0.0.0",
            "port": 7860,
            "workers": 4,
        },
        "logging": {
            "level": "INFO",
        },
        "environment": "production",
    }
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    return config_file


@pytest.fixture
def complete_config_file(tmp_path):
    """Create a complete configuration file with all providers."""
    config_file = tmp_path / "complete.yaml"
    config_data = {
        "server": {
            "host": "0.0.0.0",
            "port": 7860,
            "workers": 4,
        },
        "providers": {
            "google": {
                "api_key_env": "GOOGLE_GEMINI_KEY",
                "default_model": "gemini-1.5-pro",
                "rate_limit": 20,
                "timeout": 60
            },
            "anthropic": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "default_model": "claude-3-5-sonnet-20241022",
                "rate_limit": 20,
                "timeout": 60
            },
            "huggingface": {
                "api_key_env": "HUGGINGFACEHUB_API_TOKEN",
                "default_model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "rate_limit": 10,
                "timeout": 120
            }
        },
        "database": {
            "workflow_db": "workflow.db",
            "pool_size": 5,
            "timeout": 30
        },
        "logging": {
            "level": "INFO",
        },
        "environment": "production",
    }
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    return config_file


def test_env_var_overrides_file(base_config_file, clean_env, monkeypatch):
    """Test that environment variables override file configuration."""
    # Load base config
    monkeypatch.setenv("CONFIG_FILE", str(base_config_file))
    
    # Set environment variable override
    monkeypatch.setenv("SERVER__PORT", "9999")
    monkeypatch.setenv("SERVER__HOST", "localhost")
    
    reload_config()
    config = get_config_manager().config
    
    # Env var should override file
    assert config.server.port == 9999
    assert config.server.host == "localhost"
    # Other values from file should remain
    assert config.server.workers == 4


def test_nested_env_var_overrides(complete_config_file, clean_env, monkeypatch):
    """Test nested environment variable overrides."""
    monkeypatch.setenv("CONFIG_FILE", str(complete_config_file))
    
    # Set nested overrides
    monkeypatch.setenv("PROVIDERS__GOOGLE__RATE_LIMIT", "50")
    monkeypatch.setenv("PROVIDERS__ANTHROPIC__DEFAULT_MODEL", "claude-3-opus")
    monkeypatch.setenv("DATABASE__POOL_SIZE", "10")
    
    reload_config()
    config = get_config_manager().config
    
    assert config.providers.google.rate_limit == 50
    assert config.providers.anthropic.default_model == "claude-3-opus"
    assert config.database.pool_size == 10


def test_boolean_env_var_overrides(base_config_file, clean_env, monkeypatch):
    """Test boolean environment variable parsing."""
    monkeypatch.setenv("CONFIG_FILE", str(base_config_file))
    
    # Test boolean parsing
    monkeypatch.setenv("SERVER__RELOAD", "true")
    monkeypatch.setenv("ENABLE_METRICS", "false")
    
    reload_config()
    config = get_config_manager().config
    
    assert config.server.reload is True
    assert config.enable_metrics is False


def test_integer_env_var_overrides(base_config_file, clean_env, monkeypatch):
    """Test integer environment variable parsing."""
    monkeypatch.setenv("CONFIG_FILE", str(base_config_file))
    
    monkeypatch.setenv("SERVER__PORT", "8080")
    monkeypatch.setenv("SERVER__WORKERS", "8")
    
    reload_config()
    config = get_config_manager().config
    
    assert isinstance(config.server.port, int)
    assert config.server.port == 8080
    assert isinstance(config.server.workers, int)
    assert config.server.workers == 8


def test_string_env_var_overrides(base_config_file, clean_env, monkeypatch):
    """Test string environment variable overrides."""
    monkeypatch.setenv("CONFIG_FILE", str(base_config_file))
    
    monkeypatch.setenv("LOGGING__LEVEL", "DEBUG")
    monkeypatch.setenv("ENVIRONMENT", "development")
    
    reload_config()
    config = get_config_manager().config
    
    assert config.logging.level == "DEBUG"
    assert config.environment == "development"


def test_legacy_env_var_mapping(clean_env, monkeypatch):
    """Test that legacy environment variables are mapped correctly."""
    # Set legacy env vars
    monkeypatch.setenv("GOOGLE_GEMINI_MODEL", "gemini-1.5-flash")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-haiku")
    
    reload_config()
    config = get_config_manager().config
    
    # Legacy vars should be mapped to new config structure
    assert config.providers.google.default_model == "gemini-1.5-flash"
    assert config.providers.anthropic.default_model == "claude-3-haiku"


def test_override_priority(tmp_path, clean_env, monkeypatch):
    """Test complete override priority chain."""
    # Create config file with base values
    config_file = tmp_path / "test.yaml"
    config_data = {
        "server": {
            "port": 7860,
            "host": "0.0.0.0",
        }
    }
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    monkeypatch.setenv("CONFIG_FILE", str(config_file))
    # Environment variable should have highest priority
    monkeypatch.setenv("SERVER__PORT", "9999")
    
    reload_config()
    config = get_config_manager().config
    
    # Env var (highest priority) overrides file
    assert config.server.port == 9999
    # File value is used where no env var exists
    assert config.server.host == "0.0.0.0"
    # Built-in default is used where neither file nor env var exists
    assert config.server.workers == 4


def test_partial_overrides(base_config_file, clean_env, monkeypatch):
    """Test that partial overrides don't affect other values."""
    monkeypatch.setenv("CONFIG_FILE", str(base_config_file))
    
    # Override only one server property
    monkeypatch.setenv("SERVER__PORT", "8888")
    
    reload_config()
    config = get_config_manager().config
    
    # Overridden value
    assert config.server.port == 8888
    # Other values should remain from file
    assert config.server.host == "0.0.0.0"
    assert config.server.workers == 4


def test_validate_config_file_valid(base_config_file):
    """Test validate_config_file with valid config."""
    manager = get_config_manager()
    is_valid, error = manager.validate_config_file(base_config_file)
    
    assert is_valid is True
    assert error is None


def test_validate_config_file_invalid(tmp_path):
    """Test validate_config_file with invalid config."""
    invalid_config = tmp_path / "invalid.yaml"
    config_data = {
        "server": {
            "port": 99999,  # Invalid port
        }
    }
    with open(invalid_config, 'w') as f:
        yaml.dump(config_data, f)
    
    manager = get_config_manager()
    is_valid, error = manager.validate_config_file(invalid_config)
    
    assert is_valid is False
    assert error is not None
    assert "port" in error.lower() or "validation" in error.lower()


def test_validate_config_file_not_found():
    """Test validate_config_file with non-existent file."""
    manager = get_config_manager()
    is_valid, error = manager.validate_config_file("/nonexistent/config.yaml")
    
    assert is_valid is False
    assert error is not None
    assert "not found" in error.lower()


def test_reload_with_different_config(tmp_path, clean_env, monkeypatch):
    """Test reloading with a different configuration file."""
    # First config
    config1 = tmp_path / "config1.yaml"
    with open(config1, 'w') as f:
        yaml.dump({"server": {"port": 8001}}, f)
    
    # Second config
    config2 = tmp_path / "config2.yaml"
    with open(config2, 'w') as f:
        yaml.dump({"server": {"port": 8002}}, f)
    
    # Load first config
    monkeypatch.setenv("CONFIG_FILE", str(config1))
    reload_config()
    config = get_config_manager().config
    assert config.server.port == 8001
    
    # Reload with second config
    monkeypatch.setenv("CONFIG_FILE", str(config2))
    reload_config()
    config = get_config_manager().config
    assert config.server.port == 8002
