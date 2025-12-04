from enum import Enum
from pydantic import BaseModel, validator
from typing import Optional

class ProviderEnum(str, Enum):
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"

class GenerateRequest(BaseModel):
    name: str
    prompt: str
    task: str
    provider: ProviderEnum = ProviderEnum.ANTHROPIC
    model: str
    stream: bool = False
    db_path: Optional[str] = None

    @validator('model')
    def validate_model(cls, v, values):
        provider = values.get('provider')
        if provider == ProviderEnum.ANTHROPIC:
            allowed = [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307",
                "claude-3-5-haiku-20241022"
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
        return v
