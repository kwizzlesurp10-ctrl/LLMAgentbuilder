"""
GitHub Copilot API Client

This module provides a client for interacting with GitHub Copilot's API.
"""

import requests
from typing import List, Dict, Any, Optional


class CopilotClient:
    """
    Client for GitHub Copilot API.

    This client allows interaction with GitHub Copilot's chat completion API
    using a GitHub Personal Access Token (PAT).
    """

    def __init__(self, bearer_token: str, api_base: Optional[str] = None):
        """
        Initialize the Copilot client.

        :param bearer_token: GitHub Personal Access Token (PAT) with copilot
            scope
        :param api_base: Optional API base URL (defaults to GitHub Copilot API)
        """
        self.bearer_token = bearer_token
        self.api_base = api_base or "https://api.githubcopilot.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Get a chat completion from GitHub Copilot API.

        :param messages: List of message dictionaries with 'role' and
            'content' keys
        :param model: Optional model name (defaults to copilot's default)
        :param temperature: Optional temperature for response randomness
        :param max_tokens: Optional maximum tokens in response
        :param kwargs: Additional parameters to pass to the API
        :return: Response object with 'content' attribute
        """
        # GitHub Copilot API endpoint for chat completions
        url = f"{self.api_base}/chat/completions"

        payload = {
            "messages": messages
        }

        if model:
            payload["model"] = model
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        # Add any additional kwargs
        payload.update(kwargs)

        try:
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()

            # Create a simple response object with content attribute
            class CopilotResponse:
                def __init__(self, data: Dict[str, Any]):
                    self.data = data
                    # Extract content from response
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "message" in choice:
                            self.content = choice["message"].get(
                                "content", ""
                            )
                        else:
                            self.content = str(choice)
                    elif "content" in data:
                        self.content = data["content"]
                    else:
                        self.content = str(data)

            return CopilotResponse(data)

        except requests.exceptions.RequestException as e:
            raise Exception(
                f"GitHub Copilot API request failed: {str(e)}"
            )
        except Exception as e:
            raise Exception(
                f"Error processing Copilot response: {str(e)}"
            )

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"CopilotClient(api_base={self.api_base})"
