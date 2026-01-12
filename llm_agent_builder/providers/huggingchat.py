"""HuggingChat provider implementation."""
from typing import Dict, List
from .base import LLMProvider, register_provider


@register_provider("huggingchat")
class HuggingChatProvider(LLMProvider):
    """Provider for HuggingChat models."""
    
    def get_template_name(self) -> str:
        """Return the template for HuggingChat agents."""
        return "agent_template_huggingchat.py.j2"
    
    def validate_config(self, config: Dict) -> bool:
        """Validate HuggingChat-specific configuration."""
        model = config.get("model")
        if model and model not in self.get_supported_models():
            return False
        return True
    
    def get_env_var_name(self) -> str:
        """Return the environment variable name for HuggingChat."""
        return "HUGGINGCHAT_EMAIL"
    
    def get_default_model(self) -> str:
        """Return the default HuggingChat model."""
        return "meta-llama/Meta-Llama-3.1-70B-Instruct"
    
    def get_supported_models(self) -> List[str]:
        """Return list of supported HuggingChat models."""
        return [
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "codellama/CodeLlama-34b-Instruct-hf",
            "HuggingFaceH4/zephyr-7b-beta"
        ]
