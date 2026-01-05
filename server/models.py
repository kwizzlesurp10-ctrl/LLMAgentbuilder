from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List


class ProviderEnum(str, Enum):
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    HUGGINGCHAT = "huggingchat"


class GenerateRequest(BaseModel):
    name: str
    prompt: str
    task: str
    provider: ProviderEnum = ProviderEnum.GOOGLE
    model: str
    stream: bool = False
    db_path: Optional[str] = None
    version: Optional[str] = None  # Version identifier (auto-generated if None)
    parent_version: Optional[str] = None  # Parent version for branching

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

    @field_validator('model')
    @classmethod
    def validate_model(cls, v, info):
        provider = info.data.get('provider')
        if provider == ProviderEnum.GOOGLE:
            allowed = [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro",
                "gemini-1.0-pro"
            ]
            if v not in allowed:
                raise ValueError(f"Model {v} not supported for Google Gemini")
        elif provider == ProviderEnum.ANTHROPIC:
            allowed = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
            if v not in allowed:
                raise ValueError(f"Model {v} not supported for Anthropic")
        elif provider == ProviderEnum.HUGGINGFACE:
            allowed = [
                "meta-llama/Meta-Llama-3-8B-Instruct",
                "mistralai/Mistral-7B-Instruct-v0.3"
            ]
            if v not in allowed:
                raise ValueError(f"Model {v} not supported for Hugging Face")
        elif provider == ProviderEnum.HUGGINGCHAT:
            allowed = [
                "meta-llama/Meta-Llama-3.1-70B-Instruct",
                "meta-llama/Meta-Llama-3.1-8B-Instruct",
                "mistralai/Mistral-7B-Instruct-v0.3",
                "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "codellama/CodeLlama-34b-Instruct-hf",
                "HuggingFaceH4/zephyr-7b-beta"
            ]
            if v not in allowed:
                raise ValueError(f"Model {v} not supported for HuggingChat")
        elif provider == ProviderEnum.OPENAI:
            allowed = [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ]
            if v not in allowed:
                raise ValueError(f"Model {v} not supported for OpenAI")
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
    provider: ProviderEnum
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
    provider: ProviderEnum
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
    provider: ProviderEnum = ProviderEnum.GOOGLE
    model: str

