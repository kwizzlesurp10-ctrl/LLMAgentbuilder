"""Google Gemini provider implementation."""
from typing import Dict, List
from .base import LLMProvider, register_provider


@register_provider("google")
class GoogleGeminiProvider(LLMProvider):
    """Provider for Google Gemini models."""
    
    def get_template_name(self) -> str:
        """Return the template for Google Gemini agents."""
        return "agent_template.py.j2"
    
    def validate_config(self, config: Dict) -> bool:
        """Validate Google-specific configuration."""
        model = config.get("model")
        if model and model not in self.get_supported_models():
            return False
        return True
    
    def get_env_var_name(self) -> str:
        """Return the environment variable name for Google API key."""
        return "GOOGLE_GEMINI_KEY"
    
    def get_default_model(self) -> str:
        """Return the default Google Gemini model."""
        return "gemini-1.5-pro"
    
    def get_supported_models(self) -> List[str]:
        """Return list of supported Google Gemini models."""
        return [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-1.0-pro"
        ]
