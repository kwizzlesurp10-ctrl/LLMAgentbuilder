"""
Configuration models using Pydantic for validation.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=7860, ge=1, le=65535, description="Port to bind to")
    workers: int = Field(default=4, ge=1, description="Number of worker processes")
    timeout: int = Field(default=60, ge=1, description="Request timeout in seconds")
    reload: bool = Field(default=False, description="Enable auto-reload for development")


class ProviderConfig(BaseModel):
    """Configuration for a single LLM provider."""
    api_key_env: str = Field(..., description="Environment variable name for API key")
    default_model: str = Field(..., description="Default model to use")
    rate_limit: int = Field(default=20, ge=1, description="Requests per minute")
    timeout: int = Field(default=60, ge=1, description="Request timeout in seconds")


class ProvidersConfig(BaseModel):
    """Configuration for all LLM providers."""
    google: ProviderConfig = Field(
        default=ProviderConfig(
            api_key_env="GOOGLE_GEMINI_KEY",
            default_model="gemini-1.5-pro",
            rate_limit=20,
            timeout=60
        )
    )
    anthropic: ProviderConfig = Field(
        default=ProviderConfig(
            api_key_env="ANTHROPIC_API_KEY",
            default_model="claude-3-5-sonnet-20241022",
            rate_limit=20,
            timeout=60
        )
    )
    huggingface: Optional[ProviderConfig] = Field(
        default=ProviderConfig(
            api_key_env="HUGGINGFACEHUB_API_TOKEN",
            default_model="meta-llama/Meta-Llama-3-8B-Instruct",
            rate_limit=10,
            timeout=120
        )
    )


class DatabaseConfig(BaseModel):
    """Database configuration."""
    workflow_db: str = Field(default="workflow.db", description="Workflow database path")
    pool_size: int = Field(default=5, ge=1, description="Connection pool size")
    timeout: int = Field(default=30, ge=1, description="Connection timeout in seconds")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file: Optional[str] = Field(default=None, description="Log file path (None for console only)")
    max_bytes: int = Field(default=10485760, description="Max log file size in bytes (10MB)")
    backup_count: int = Field(default=5, description="Number of backup log files")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid logging level: {v}. Must be one of {valid_levels}")
        return v_upper


class AppConfig(BaseModel):
    """Master application configuration."""
    server: ServerConfig = Field(default_factory=ServerConfig)
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    environment: str = Field(default="production", description="Environment name (dev/staging/prod)")
    
    # Additional application-specific settings
    generated_agents_dir: str = Field(default="generated_agents", description="Directory for generated agents")
    template_dir: Optional[str] = Field(default=None, description="Custom template directory")
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment name."""
        valid_envs = ["development", "staging", "production", "test"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return v.lower()

    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider."""
        return getattr(self.providers, provider.lower(), None)

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider from environment."""
        import os
        provider_config = self.get_provider_config(provider)
        if provider_config:
            return os.environ.get(provider_config.api_key_env)
        return None
