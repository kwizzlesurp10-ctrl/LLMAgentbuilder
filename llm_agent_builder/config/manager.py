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
    
    def _load_config_files(self, config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Load configuration files with proper cascading.
        
        Returns merged configuration from:
        1. default.yaml (base)
        2. environment-specific yaml (overrides)
        
        If explicit config_path is provided or CONFIG_FILE env var is set, 
        only that file is loaded without cascading.
        """
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"
        
        config_dict: Dict[str, Any] = {}
        
        # Check if explicit path provided or CONFIG_FILE env var is set
        explicit_config = config_path or os.environ.get("CONFIG_FILE")
        if explicit_config:
            path = Path(explicit_config)
            if path.exists():
                logger.info(f"Loading explicit configuration file: {path}")
                if path.suffix in (".yaml", ".yml"):
                    return self._load_yaml(path)
                elif path.suffix == ".json":
                    return self._load_json(path)
            else:
                logger.warning(f"Explicit config file not found: {path}")
            return config_dict
        
        # Load default.yaml if it exists (base configuration)
        default_config_file = config_dir / "default.yaml"
        if default_config_file.exists():
            logger.info(f"Loading default configuration: {default_config_file}")
            config_dict = self._load_yaml(default_config_file)
        
        # Load environment-specific config if it exists (overrides default)
        environment = os.environ.get("ENVIRONMENT", os.environ.get("ENV", "production")).lower()
        env_config_file = config_dir / f"{environment}.yaml"
        if env_config_file.exists() and env_config_file != default_config_file:
            logger.info(f"Loading environment-specific config: {env_config_file}")
            env_config = self._load_yaml(env_config_file)
            config_dict = self._merge_config(config_dict, env_config)
        
        return config_dict
    
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
        import copy
        result = copy.deepcopy(base)
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
        
        Also handles top-level keys like ENVIRONMENT directly.
        """
        import copy
        # Start with a copy of the base config
        result = copy.deepcopy(config_dict)
        
        # Build env overrides as a separate dict, then merge
        env_overrides: Dict[str, Any] = {}
        
        # Helper to parse value
        def parse_value(val: str) -> Any:
            """Parse string value to appropriate type."""
            try:
                # Try boolean first (case-insensitive)
                if val.lower() in ("true", "false"):
                    return val.lower() == "true"
                
                # Try integer (including negative)
                try:
                    return int(val)
                except ValueError:
                    pass
                
                # Try float
                try:
                    return float(val)
                except ValueError:
                    pass
                
                # Return as string
                return val
            except (AttributeError, TypeError):
                return val
        
        # Process all environment variables
        for env_key, env_value in os.environ.items():
            if "__" in env_key:
                # Nested key with double underscore
                parts = env_key.lower().split("__")
                
                # Build nested dict in env_overrides
                current = env_overrides
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = parse_value(env_value)
            else:
                # Check if this is a top-level config key (lowercase to match)
                key_lower = env_key.lower()
                # Only handle known top-level keys to avoid polluting config
                top_level_keys = [
                    "environment", "generated_agents_dir", "template_dir", 
                    "enable_metrics", "enable_rate_limiting"
                ]
                if key_lower in top_level_keys:
                    env_overrides[key_lower] = parse_value(env_value)
        
        # Merge env overrides with result
        result = self._merge_config(result, env_overrides)
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
        # Load config files with proper cascading
        config_dict = self._load_config_files(config_path)
        
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
                # Navigate and create nested structure if needed
                current = config_dict
                for part in path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                # Set the value (overrides existing)
                current[path[-1]] = value
        
        # Validate and create AppConfig
        try:
            config = AppConfig(**config_dict)
            logger.info(f"Configuration loaded successfully (environment: {config.environment})")
            return config
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            # Log config structure without sensitive values
            if logger.isEnabledFor(logging.DEBUG):
                safe_dict = self._sanitize_config_for_logging(config_dict)
                logger.debug(f"Config dict (sanitized): {safe_dict}")
            raise
    
    def _sanitize_config_for_logging(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from config dict for logging."""
        import copy
        safe_dict = copy.deepcopy(config_dict)
        
        # Remove provider details (could contain sensitive info)
        if "providers" in safe_dict and isinstance(safe_dict["providers"], dict):
            for provider, settings in safe_dict["providers"].items():
                if isinstance(settings, dict):
                    safe_dict["providers"][provider] = {
                        k: "***" if k in ("api_key", "api_key_env", "api_secret") else v
                        for k, v in settings.items()
                    }
        
        # Remove database credentials if any
        if "database" in safe_dict and isinstance(safe_dict["database"], dict):
            db_settings = safe_dict["database"]
            for key in list(db_settings.keys()):
                if any(word in key.lower() for word in ["password", "secret", "credential"]):
                    db_settings[key] = "***"
        
        return safe_dict
    
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
