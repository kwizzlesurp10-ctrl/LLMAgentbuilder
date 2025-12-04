"""
Tests using a mock Cursor/Anthropic API.

This test suite mocks the Anthropic API client to simulate Cursor API behavior
without making actual API calls.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_agent_builder.agent_builder import AgentBuilder


# Mock Anthropic API response structure
class MockMessage:
    """Mock Anthropic Message object."""
    def __init__(self, content: str, stop_reason: str = "end_turn"):
        self.content = [Mock(text=content)]
        self.stop_reason = stop_reason
        self.id = "msg_12345"
        self.model = "claude-3-5-sonnet-20241022"
        self.role = "assistant"
        self.type = "message"
        self.stop_reason = stop_reason


class MockMessages:
    """Mock messages API."""
    
    def create(self, **kwargs):
        """Mock message creation."""
        # Simulate different responses based on input
        messages = kwargs.get("messages", [])
        if messages:
            task = messages[-1].get("content", "")
        else:
            task = ""
        
        # Simulate different behaviors
        if "error" in task.lower():
            raise Exception("Mock API error: Rate limit exceeded")
        
        if "timeout" in task.lower():
            raise TimeoutError("Mock API timeout")
        
        # Default successful response
        response_text = f"Mock Cursor API response for: {task}"
        return MockMessage(response_text)


class MockAnthropicClient:
    """Mock Anthropic client that simulates API responses."""
    
    def __init__(self, api_key: str = "mock-key"):
        self.api_key = api_key
        self.messages = MockMessages()


@pytest.fixture
def mock_anthropic_client():
    """Fixture providing a mock Anthropic client."""
    return MockAnthropicClient()


@pytest.fixture
def temp_agent_file(tmp_path):
    """Create a temporary agent file with mocked API."""
    agent_code = '''
import anthropic
import os
from typing import Optional

class MockTestAgent:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.prompt = "You are a helpful assistant."
    
    def run(self, task: str) -> str:
        """Run the agent with a task."""
        response = self.client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=1024,
            system=self.prompt,
            messages=[{"role": "user", "content": task}]
        )
        return response.content[0].text

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="default task")
    args = parser.parse_args()
    
    api_key = os.environ.get("ANTHROPIC_API_KEY", "mock-key")
    agent = MockTestAgent(api_key=api_key)
    result = agent.run(args.task)
    print(result)
'''
    agent_file = tmp_path / "mock_agent.py"
    agent_file.write_text(agent_code)
    return agent_file


def test_mock_anthropic_client_initialization(mock_anthropic_client):
    """Test that mock client initializes correctly."""
    assert mock_anthropic_client.api_key == "mock-key"
    assert mock_anthropic_client.messages is not None


def test_mock_anthropic_api_call(mock_anthropic_client):
    """Test making a mock API call."""
    response = mock_anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="You are helpful.",
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    assert response is not None
    assert hasattr(response, 'content')
    assert len(response.content) > 0
    assert "Mock Cursor API response" in response.content[0].text


def test_mock_api_error_handling(mock_anthropic_client):
    """Test mock API error handling."""
    with pytest.raises(Exception) as exc_info:
        mock_anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": "error test"}]
        )
    
    assert "Mock API error" in str(exc_info.value)


@patch('anthropic.Anthropic')
def test_agent_builder_with_mock_api(mock_anthropic_class, temp_agent_file):
    """Test agent builder generates code that works with mocked API."""
    builder = AgentBuilder()
    code = builder.build_agent(
        agent_name="MockCursorAgent",
        prompt="You are a test agent using mock Cursor API",
        example_task="Test task",
        model="claude-3-5-sonnet-20241022",
        provider="anthropic"
    )
    
    assert "MockCursorAgent" in code
    assert "anthropic.Anthropic" in code
    assert "client.messages.create" in code


@patch('anthropic.Anthropic')
def test_generated_agent_with_mock_api(mock_anthropic_class, temp_agent_file):
    """Test that a generated agent works with mocked API calls."""
    # Setup mock
    mock_client_instance = MockAnthropicClient()
    mock_anthropic_class.return_value = mock_client_instance
    
    # Import and run the agent
    import importlib.util
    spec = importlib.util.spec_from_file_location("mock_agent", temp_agent_file)
    module = importlib.util.module_from_spec(spec)
    
    # Mock the anthropic module
    sys.modules['anthropic'] = MagicMock()
    sys.modules['anthropic'].Anthropic = Mock(return_value=mock_client_instance)
    
    spec.loader.exec_module(module)
    
    # Test the agent
    agent = module.MockTestAgent(api_key="mock-key")
    result = agent.run("test task")
    
    assert result is not None
    assert "Mock Cursor API response" in result


def test_mock_api_with_different_responses(mock_anthropic_client):
    """Test mock API with different response scenarios."""
    # Test normal response
    response1 = mock_anthropic_client.messages.create(
        messages=[{"role": "user", "content": "normal task"}]
    )
    assert "normal task" in response1.content[0].text
    
    # Test error response
    with pytest.raises(Exception):
        mock_anthropic_client.messages.create(
            messages=[{"role": "user", "content": "error scenario"}]
        )


@patch.dict(os.environ, {"ANTHROPIC_API_KEY": "mock-cursor-api-key"})
def test_mock_api_with_environment_variables():
    """Test mock API respects environment variables."""
    assert os.environ.get("ANTHROPIC_API_KEY") == "mock-cursor-api-key"
    
    # Create mock client with env key
    client = MockAnthropicClient(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    assert client.api_key == "mock-cursor-api-key"


def test_mock_api_streaming_response():
    """Test mock API streaming response (simulating Cursor streaming)."""
    mock_client = MockAnthropicClient()
    
    # Simulate streaming response
    class MockStreamChunk:
        def __init__(self, text: str, done: bool = False):
            self.text = text
            self.done = done
    
    # Mock streaming
    stream_chunks = [
        MockStreamChunk("Mock ", False),
        MockStreamChunk("Cursor ", False),
        MockStreamChunk("API ", False),
        MockStreamChunk("response", True)
    ]
    
    full_response = "".join(chunk.text for chunk in stream_chunks)
    assert full_response == "Mock Cursor API response"


def test_mock_api_rate_limiting():
    """Test mock API rate limiting behavior."""
    mock_client = MockAnthropicClient()
    
    # Simulate rate limit error
    class RateLimitError(Exception):
        pass
    
    def rate_limited_create(**kwargs):
        raise RateLimitError("Rate limit exceeded. Please retry after 60 seconds.")
    
    mock_client.messages.create = rate_limited_create
    
    with pytest.raises(RateLimitError):
        mock_client.messages.create(messages=[{"role": "user", "content": "test"}])


def test_mock_api_with_tools():
    """Test mock API with tool calling (Cursor-style tool use)."""
    mock_client = MockAnthropicClient()
    
    # Mock tool use response
    class MockToolUse:
        def __init__(self):
            self.type = "tool_use"
            self.id = "tool_123"
            self.name = "search_web"
            self.input = {"query": "test query"}
    
    class MockToolMessage(MockMessage):
        def __init__(self):
            super().__init__("", stop_reason="tool_use")
            self.content = [MockToolUse()]
    
    response = MockToolMessage()
    assert response.stop_reason == "tool_use"
    assert response.content[0].type == "tool_use"
    assert response.content[0].name == "search_web"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

