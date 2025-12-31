"""
HuggingChat Client - Integration with HuggingChat API

This module provides a client for interacting with HuggingChat,
the conversational AI interface from Hugging Face.
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class HuggingChatMessage:
    """Represents a message in a HuggingChat conversation."""
    role: str  # 'user' or 'assistant'
    content: str


class HuggingChatClient:
    """
    Client for HuggingChat API integration.
    
    HuggingChat provides access to various open-source LLMs including:
    - Meta-Llama models
    - Mistral models
    - CodeLlama models
    - And other community models
    """
    
    # Default models available on HuggingChat
    DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct"
    
    AVAILABLE_MODELS = [
        "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "codellama/CodeLlama-34b-Instruct-hf",
        "HuggingFaceH4/zephyr-7b-beta",
    ]
    
    def __init__(
        self,
        token: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize HuggingChat client.
        
        :param token: HuggingFace API token (optional for public models)
        :param model: Model to use (default: Meta-Llama-3.1-70B-Instruct)
        """
        self.token = token or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        self.model = model or os.environ.get("HUGGINGCHAT_MODEL", self.DEFAULT_MODEL)
        self.conversation_history: List[HuggingChatMessage] = []
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> str:
        """
        Send a chat message and get response.
        
        :param message: User message
        :param system_prompt: Optional system prompt to guide behavior
        :param temperature: Sampling temperature (0.0 to 1.0)
        :param max_tokens: Maximum tokens to generate
        :param stream: Whether to stream the response
        :return: Assistant's response
        """
        # Use Hugging Face Inference API as HuggingChat web interface
        # doesn't have a public API yet
        from huggingface_hub import InferenceClient
        
        client = InferenceClient(token=self.token)
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        for msg in self.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            if stream:
                response_text = ""
                for chunk in client.chat_completion(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                ):
                    if chunk and hasattr(chunk, 'choices') and chunk.choices:
                        delta = chunk.choices[0].delta
                        if delta and hasattr(delta, 'content') and delta.content:
                            response_text += delta.content
                            print(delta.content, end="", flush=True)
                print()  # Newline after stream
                result = response_text
            else:
                response = client.chat_completion(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=False
                )
                if response and hasattr(response, 'choices') and response.choices:
                    result = response.choices[0].message.content
                else:
                    raise RuntimeError("Invalid response from HuggingChat")
            
            # Update conversation history
            self.conversation_history.append(
                HuggingChatMessage(role="user", content=message)
            )
            self.conversation_history.append(
                HuggingChatMessage(role="assistant", content=result)
            )
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"HuggingChat API error: {e}")
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_available_models(self) -> List[str]:
        """Get list of available models on HuggingChat."""
        return self.AVAILABLE_MODELS
    
    def search_models(
        self,
        query: str,
        task: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for models on Hugging Face Hub.
        
        :param query: Search query
        :param task: Filter by task (e.g., 'text-generation', 'conversational')
        :param limit: Maximum number of results
        :return: List of model information
        """
        from huggingface_hub import HfApi
        
        api = HfApi(token=self.token)
        models = api.list_models(
            search=query,
            task=task,
            limit=limit,
            sort="downloads",
            direction=-1
        )
        
        return [
            {
                "id": model.modelId,
                "downloads": getattr(model, 'downloads', 0),
                "likes": getattr(model, 'likes', 0),
                "tags": getattr(model, 'tags', []),
            }
            for model in models
        ]


def create_huggingchat_agent(
    agent_name: str,
    system_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Factory function to create a HuggingChat-based agent class.
    
    :param agent_name: Name of the agent class
    :param system_prompt: System prompt for the agent
    :param model: Model to use (default: Meta-Llama-3.1-70B-Instruct)
    :param temperature: Sampling temperature
    :return: Python code for the agent class
    """
    model = model or HuggingChatClient.DEFAULT_MODEL
    
    code = f'''"""
{agent_name} - HuggingChat-powered Agent
Generated by LLM Agent Builder
"""

import os
from typing import Optional
from llm_agent_builder.huggingchat_client import HuggingChatClient


class {agent_name}:
    """
    {agent_name} agent powered by HuggingChat.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the {agent_name}.
        
        :param token: HuggingFace API token (optional)
        """
        self.client = HuggingChatClient(
            token=token,
            model="{model}"
        )
        self.system_prompt = """{system_prompt}"""
        
    def run(self, task: str, stream: bool = False) -> str:
        """
        Execute a task with the agent.
        
        :param task: Task to perform
        :param stream: Whether to stream the response
        :return: Agent's response
        """
        return self.client.chat(
            message=task,
            system_prompt=self.system_prompt,
            temperature={temperature},
            stream=stream
        )
    
    def clear_history(self):
        """Clear conversation history."""
        self.client.clear_history()


if __name__ == '__main__':
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Run {agent_name}")
    parser.add_argument("--task", required=True, help="Task to perform")
    parser.add_argument("--stream", action="store_true", help="Stream response")
    args = parser.parse_args()
    
    agent = {agent_name}()
    result = agent.run(args.task, stream=args.stream)
    
    if not args.stream:
        print("\\nResponse:")
        print("-" * 50)
        print(result)
        print("-" * 50)
'''
    
    return code
