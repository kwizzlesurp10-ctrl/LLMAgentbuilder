from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
from llm_agent_builder.providers import ProviderRegistry


# Dynamically generate ProviderEnum from registered providers
def _create_provider_enum():
    """Create a dynamic Enum from registered providers."""
    provider_names = ProviderRegistry.get_all_names()
    members = {name.upper(): name for name in provider_names}
    return Enum('ProviderEnum', members, type=str)


ProviderEnum = _create_provider_enum()


class GenerateRequest(BaseModel):
    name: str
    prompt: str
    task: str
    provider: str = "google"  # String allows dynamic provider registration without code changes
    model: str
    stream: bool = False
    db_path: Optional[str] = None
    version: Optional[str] = None  # Version identifier (auto-generated if None)
    parent_version: Optional[str] = None  # Parent version for branching
    enable_multi_step: bool = False  # Enable multi-step workflow capabilities
    tools: Optional[List[Dict[str, Any]]] = None  # List of tool definitions for tool calling

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        # Ensure name is a valid Python class name
        trimmed = v.strip()
        if not trimmed[0].isalpha() and trimmed[0] != '_':
            raise ValueError("Agent name must start with a letter or underscore")
        return trimmed

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        """Validate that the provider is registered."""
        if not ProviderRegistry.is_registered(v):
            available = ', '.join(ProviderRegistry.get_all_names())
            raise ValueError(f"Provider '{v}' not supported. Available providers: {available}")
        return v

    @field_validator('model')
    @classmethod
    def validate_model(cls, v, info):
        """Validate model using provider's supported models list."""
        provider_name = info.data.get('provider')
        if not provider_name:
            return v
        
        # Check if provider exists first
        if not ProviderRegistry.is_registered(provider_name):
            # Let the provider validator handle this
            return v
        
        provider = ProviderRegistry.get(provider_name)
        supported_models = provider.get_supported_models()
        if v not in supported_models:
            models_list = ', '.join(supported_models)
            raise ValueError(f"Model '{v}' not supported for {provider_name}. "
                           f"Supported models: {models_list}")
        
        return v


class TestAgentRequest(BaseModel):
    """Request model for testing an agent."""
    agent_code: Optional[str] = None
    agent_path: Optional[str] = None
    task: str
    timeout: Optional[int] = 60


class AgentVersion(BaseModel):
    """Model representing an agent version."""
    id: str
    name: str
    version: str
    parent_version: Optional[str]
    prompt: str
    task: str
    provider: str
    model: str
    code: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = {}


class AgentVersionResponse(BaseModel):
    """Response model for agent version operations."""
    versions: List[AgentVersion]
    total: int
    page: int = 1
    page_size: int = 10


class AgentExport(BaseModel):
    """Model for exporting agent configuration."""
    name: str
    prompt: str
    task: str
    provider: str
    model: str
    stream: bool = False
    version: Optional[str] = None
    exported_at: str
    metadata: Optional[Dict[str, Any]] = {}


class AgentImportRequest(BaseModel):
    """Request model for importing agent configuration."""
    config: AgentExport


class EnhancePromptRequest(BaseModel):
    """Request model for enhancing a system prompt."""
    keyword: str
    provider: str = "google"
    model: str

