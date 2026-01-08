"""HuggingFace provider implementation."""
from typing import Dict, List
from .base import LLMProvider, register_provider


@register_provider("huggingface")
class HuggingFaceProvider(LLMProvider):
    """Provider for HuggingFace models."""
    
    def get_template_name(self) -> str:
        """Return the template for HuggingFace agents."""
        return "agent_template_hf.py.j2"
    
    def validate_config(self, config: Dict) -> bool:
        """Validate HuggingFace-specific configuration."""
        model = config.get("model")
        if model and model not in self.get_supported_models():
            return False
        return True
    
    def get_env_var_name(self) -> str:
        """Return the environment variable name for HuggingFace API key."""
        return "HUGGINGFACEHUB_API_TOKEN"
    
    def get_default_model(self) -> str:
        """Return the default HuggingFace model."""
        return "meta-llama/Meta-Llama-3-8B-Instruct"
    
    def get_supported_models(self) -> List[str]:
        """Return list of supported HuggingFace models."""
        return [
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3"
        ]
