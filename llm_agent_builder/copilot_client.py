"""
GitHub Copilot API Client with Bearer token authentication.

This module provides a mock GitHub Copilot API client for testing and development.
"""

from typing import Optional, List, Dict, Any


class CopilotCompletion:
    """GitHub Copilot completion response."""
    def __init__(self, text: str, completion_id: str = "comp_12345"):
        self.text = text
        self.completion_id = completion_id
        self.finish_reason = "stop"
        self.index = 0


class CopilotChatMessage:
    """GitHub Copilot chat message."""
    def __init__(self, content: str, role: str = "assistant"):
        self.content = content
        self.role = role
        self.timestamp = "2024-01-01T00:00:00Z"


class CopilotClient:
    """GitHub Copilot API client with Bearer token authentication."""
    
    BASE_URL = "https://api.githubcopilot.com"
    
    def __init__(self, bearer_token: str):
        """
        Initialize GitHub Copilot client.
        
        :param bearer_token: Bearer token for authentication
        """
        if not bearer_token:
            raise ValueError("Bearer token is required")
        self.bearer_token = bearer_token
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self._request_count = 0
    
    def _validate_token(self):
        """Validate bearer token format."""
        if not self.bearer_token.startswith(("Bearer ", "ghp_", "github_pat_")):
            # Accept tokens that start with Bearer or GitHub token prefixes
            if not any(self.bearer_token.startswith(prefix) for prefix in ["Bearer ", "ghp_", "github_pat_", "mock-"]):
                raise ValueError("Invalid bearer token format")
    
    def get_completions(self, prompt: str, max_tokens: int = 100, **kwargs) -> List[CopilotCompletion]:
        """
        Get code completions from GitHub Copilot API.
        
        :param prompt: Code prompt
        :param max_tokens: Maximum tokens to generate
        :return: List of completions
        """
        self._validate_token()
        self._request_count += 1
        
        # Simulate different behaviors
        if "error" in prompt.lower():
            raise Exception("Mock API error: Invalid request")
        
        if "rate_limit" in prompt.lower():
            raise Exception("Mock API error: Rate limit exceeded")
        
        if "unauthorized" in prompt.lower():
            raise Exception("Mock API error: Unauthorized - Invalid bearer token")
        
        # Default successful response
        completion_text = f"// Mock GitHub Copilot completion for: {prompt[:50]}..."
        return [CopilotCompletion(completion_text)]
    
    def get_chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-4", **kwargs) -> CopilotChatMessage:
        """
        Get chat completion from GitHub Copilot API.
        
        :param messages: List of message dictionaries
        :param model: Model to use
        :return: Chat completion response
        """
        self._validate_token()
        self._request_count += 1
        
        # Extract user message
        user_message = next((msg for msg in messages if msg.get("role") == "user"), {})
        content = user_message.get("content", "")
        
        # Simulate different behaviors
        if "error" in content.lower():
            raise Exception("Mock API error: Invalid request")
        
        if "rate_limit" in content.lower():
            raise Exception("Mock API error: Rate limit exceeded")
        
        # Default successful response
        response_text = f"Mock GitHub Copilot response: {content[:100]}"
        return CopilotChatMessage(response_text, role="assistant")
    
    def get_code_suggestions(self, file_path: str, cursor_position: Dict[str, int], context: str = "") -> List[str]:
        """
        Get code suggestions from GitHub Copilot API.
        
        :param file_path: Path to the file
        :param cursor_position: Cursor position (line, character)
        :param context: Code context
        :return: List of code suggestions
        """
        self._validate_token()
        self._request_count += 1
        
        suggestions = [
            f"// Suggestion 1 for {file_path} at line {cursor_position.get('line', 0)}",
            f"// Suggestion 2 for {file_path} at line {cursor_position.get('line', 0)}"
        ]
        return suggestions
    
    def get_request_count(self) -> int:
        """Get the number of API requests made."""
        return self._request_count

