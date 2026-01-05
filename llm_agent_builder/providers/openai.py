"""OpenAI provider implementation."""
from typing import Dict, List
from .base import LLMProvider, register_provider


@register_provider("openai")
class OpenAIProvider(LLMProvider):
    """Provider for OpenAI models."""
    
    def get_template_name(self) -> str:
        """Return the template for OpenAI agents."""
        return "agent_template_openai.py.j2"
    
    def validate_config(self, config: Dict) -> bool:
        """Validate OpenAI-specific configuration."""
        model = config.get("model")
        if model and model not in self.get_supported_models():
            return False
        return True
    
    def get_env_var_name(self) -> str:
        """Return the environment variable name for OpenAI API key."""
        return "OPENAI_API_KEY"
    
    def get_default_model(self) -> str:
        """Return the default OpenAI model."""
        return "gpt-4o"
    
    def get_supported_models(self) -> List[str]:
        """Return list of supported OpenAI models."""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
