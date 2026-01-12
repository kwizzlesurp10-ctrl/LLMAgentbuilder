"""
Configuration management module.

This module provides comprehensive configuration management with YAML support,
environment variable overrides, and validation.

Usage:
    from llm_agent_builder.config import get_config, load_config
    
    # Get configuration
    config = get_config()
    
    # Access configuration values
    port = config.server.port
    api_key = config.get_api_key("google")
    
    # Or use the manager directly
    from llm_agent_builder.config import get_config_manager
    
    manager = get_config_manager()
    value = manager.get("server.port")
"""

from .models import (
    AppConfig,
    ServerConfig,
    ProviderConfig,
    ProvidersConfig,
    DatabaseConfig,
    LoggingConfig,
)

from .manager import (
    ConfigManager,
    get_config_manager,
    get_config,
    reload_config,
)

__all__ = [
    # Models
    "AppConfig",
    "ServerConfig",
    "ProviderConfig",
    "ProvidersConfig",
    "DatabaseConfig",
    "LoggingConfig",
    # Manager functions
    "ConfigManager",
    "get_config_manager",
    "get_config",
    "reload_config",
    "load_config",
]


# Convenience alias
def load_config(config_path=None):
    """
    Load or reload configuration.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        AppConfig instance
    """
    if config_path:
        reload_config(config_path)
    return get_config()
