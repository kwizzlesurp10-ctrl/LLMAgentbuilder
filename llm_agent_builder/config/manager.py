"""
Configuration manager with support for YAML, JSON, and environment variables.
"""
import os
import yaml
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from .models import AppConfig

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Configuration manager implementing singleton pattern.
    
    Supports hierarchical configuration loading:
    1. Built-in defaults (in Pydantic models)
    2. Default YAML file (config/default.yaml)
    3. Environment-specific YAML (config/{ENV}.yaml)
    4. Environment variables (highest priority)
    """
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AppConfig] = None
    _config_file: Optional[Path] = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        # Only initialize once
        if self._config is None:
            self._config = self._load_config()
    
    @property
    def config(self) -> AppConfig:
        """Get the current configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _find_config_file(self, config_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
        """
        Find configuration file.
        
        Priority:
        1. Explicit config_path parameter
        2. CONFIG_FILE environment variable
        3. Environment-specific file (config/{ENV}.yaml)
        4. Default file (config/default.yaml)
        """
        # Check explicit path
        if config_path:
            path = Path(config_path)
            if path.exists():
                logger.info(f"Using configuration file: {path}")
                return path
            else:
                logger.warning(f"Configuration file not found: {path}")
        
        # Check environment variable
        env_config_file = os.environ.get("CONFIG_FILE")
        if env_config_file:
            path = Path(env_config_file)
            if path.exists():
                logger.info(f"Using configuration file from CONFIG_FILE env: {path}")
                return path
        
        # Determine project root (go up from llm_agent_builder/config to project root)
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"
        
        # Check environment-specific file
        environment = os.environ.get("ENVIRONMENT", os.environ.get("ENV", "production")).lower()
        env_config_file = config_dir / f"{environment}.yaml"
        if env_config_file.exists():
            logger.info(f"Using environment-specific config: {env_config_file}")
            return env_config_file
        
        # Check default file
        default_config_file = config_dir / "default.yaml"
        if default_config_file.exists():
            logger.info(f"Using default configuration: {default_config_file}")
            return default_config_file
        
        # No config file found
        logger.info("No configuration file found, using built-in defaults")
        return None
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            logger.error(f"Error loading YAML file {file_path}: {e}")
            raise
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            raise
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _apply_env_overrides(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides.
        
        Environment variables can override config values using double underscore notation:
        - SERVER__HOST -> config["server"]["host"]
        - PROVIDERS__GOOGLE__RATE_LIMIT -> config["providers"]["google"]["rate_limit"]
        """
        result = config_dict.copy()
        
        # Collect all env vars that match our pattern
        for env_key, env_value in os.environ.items():
            if "__" in env_key:
                # Convert env var to nested dict path
                parts = env_key.lower().split("__")
                
                # Navigate to the nested location
                current = result
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    elif not isinstance(current[part], dict):
                        # Can't override non-dict value
                        continue
                    current = current[part]
                
                # Set the value (try to parse as bool/int/float if possible)
                key = parts[-1]
                try:
                    # Try boolean
                    if env_value.lower() in ("true", "false"):
                        current[key] = env_value.lower() == "true"
                    # Try integer
                    elif env_value.isdigit():
                        current[key] = int(env_value)
                    # Try float
                    elif "." in env_value and env_value.replace(".", "").replace("-", "").isdigit():
                        current[key] = float(env_value)
                    else:
                        current[key] = env_value
                except (ValueError, AttributeError):
                    current[key] = env_value
        
        return result
    
    def _load_config(self, config_path: Optional[Union[str, Path]] = None) -> AppConfig:
        """
        Load configuration from files and environment.
        
        Priority (highest to lowest):
        1. Environment variables
        2. Environment-specific config file
        3. Default config file
        4. Built-in defaults
        """
        config_dict: Dict[str, Any] = {}
        
        # Find and load config file
        config_file = self._find_config_file(config_path)
        if config_file:
            self._config_file = config_file
            
            if config_file.suffix == ".yaml" or config_file.suffix == ".yml":
                file_config = self._load_yaml(config_file)
            elif config_file.suffix == ".json":
                file_config = self._load_json(config_file)
            else:
                logger.warning(f"Unsupported config file format: {config_file.suffix}")
                file_config = {}
            
            config_dict = file_config
        
        # Apply environment variable overrides
        config_dict = self._apply_env_overrides(config_dict)
        
        # Also check for legacy env vars and map them
        legacy_env_mapping = {
            "GOOGLE_GEMINI_MODEL": ("providers", "google", "default_model"),
            "ANTHROPIC_MODEL": ("providers", "anthropic", "default_model"),
        }
        
        for env_var, path in legacy_env_mapping.items():
            value = os.environ.get(env_var)
            if value:
                current = config_dict
                for part in path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[path[-1]] = value
        
        # Validate and create AppConfig
        try:
            config = AppConfig(**config_dict)
            logger.info(f"Configuration loaded successfully (environment: {config.environment})")
            return config
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            raise
    
    def reload(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """
        Reload configuration from files.
        
        Useful for development/testing with hot-reload.
        """
        logger.info("Reloading configuration...")
        self._config = self._load_config(config_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Example:
            config.get("server.port")
            config.get("providers.google.default_model")
        """
        parts = key.split(".")
        value = self.config.model_dump()
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def validate_config_file(self, config_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
        """
        Validate a configuration file without loading it.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            path = Path(config_path)
            if not path.exists():
                return False, f"File not found: {config_path}"
            
            # Load file
            if path.suffix in (".yaml", ".yml"):
                config_dict = self._load_yaml(path)
            elif path.suffix == ".json":
                config_dict = self._load_json(path)
            else:
                return False, f"Unsupported file format: {path.suffix}"
            
            # Validate with Pydantic
            AppConfig(**config_dict)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return self.config.model_dump()
    
    def to_yaml(self) -> str:
        """Export configuration as YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
    
    def to_json(self) -> str:
        """Export configuration as JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# Global instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Get the global configuration."""
    return get_config_manager().config


def reload_config(config_path: Optional[Union[str, Path]] = None) -> None:
    """Reload the global configuration."""
    get_config_manager().reload(config_path)
