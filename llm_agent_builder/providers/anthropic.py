"""Anthropic provider implementation."""
from typing import Dict, List
from .base import LLMProvider, register_provider


@register_provider("anthropic")
class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude models."""
    
    def get_template_name(self) -> str:
        """Return the template for Anthropic agents."""
        return "agent_template.py.j2"
    
    def validate_config(self, config: Dict) -> bool:
        """Validate Anthropic-specific configuration."""
        model = config.get("model")
        if model and model not in self.get_supported_models():
            return False
        return True
    
    def get_env_var_name(self) -> str:
        """Return the environment variable name for Anthropic API key."""
        return "ANTHROPIC_API_KEY"
    
    def get_default_model(self) -> str:
        """Return the default Anthropic model."""
        return "claude-3-5-sonnet-20241022"
    
    def get_supported_models(self) -> List[str]:
        """Return list of supported Anthropic models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
