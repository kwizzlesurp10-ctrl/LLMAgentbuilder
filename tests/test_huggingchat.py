"""
Tests for HuggingChat client integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from llm_agent_builder.huggingchat_client import (
    HuggingChatClient,
    HuggingChatMessage,
    create_huggingchat_agent
)


def test_huggingchat_message():
    """Test HuggingChatMessage dataclass."""
    msg = HuggingChatMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"


def test_huggingchat_client_init():
    """Test HuggingChatClient initialization."""
    client = HuggingChatClient(token="test_token")
    assert client.token == "test_token"
    assert client.model == HuggingChatClient.DEFAULT_MODEL
    assert len(client.conversation_history) == 0


def test_huggingchat_client_default_token():
    """Test HuggingChatClient with environment token."""
    with patch.dict('os.environ', {'HUGGINGFACEHUB_API_TOKEN': 'env_token'}):
        client = HuggingChatClient()
        assert client.token == "env_token"


def test_get_available_models():
    """Test getting available models."""
    client = HuggingChatClient(token="test_token")
    models = client.get_available_models()
    assert isinstance(models, list)
    assert len(models) > 0
    assert HuggingChatClient.DEFAULT_MODEL in models


@patch('huggingface_hub.InferenceClient')
def test_chat_non_streaming(mock_inference_client):
    """Test chat without streaming."""
    # Mock the response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Test response"
    
    mock_client = Mock()
    mock_client.chat_completion.return_value = mock_response
    mock_inference_client.return_value = mock_client
    
    client = HuggingChatClient(token="test_token")
    response = client.chat("Hello", stream=False)
    
    assert response == "Test response"
    assert len(client.conversation_history) == 2
    assert client.conversation_history[0].role == "user"
    assert client.conversation_history[0].content == "Hello"
    assert client.conversation_history[1].role == "assistant"
    assert client.conversation_history[1].content == "Test response"


@patch('huggingface_hub.InferenceClient')
def test_chat_with_system_prompt(mock_inference_client):
    """Test chat with system prompt."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Response"
    
    mock_client = Mock()
    mock_client.chat_completion.return_value = mock_response
    mock_inference_client.return_value = mock_client
    
    client = HuggingChatClient(token="test_token")
    response = client.chat(
        "Hello",
        system_prompt="You are helpful",
        stream=False
    )
    
    # Verify chat_completion was called with system message
    call_args = mock_client.chat_completion.call_args
    messages = call_args[1]['messages']
    assert messages[0]['role'] == 'system'
    assert messages[0]['content'] == 'You are helpful'


def test_clear_history():
    """Test clearing conversation history."""
    client = HuggingChatClient(token="test_token")
    client.conversation_history = [
        HuggingChatMessage(role="user", content="Hello"),
        HuggingChatMessage(role="assistant", content="Hi")
    ]
    
    client.clear_history()
    assert len(client.conversation_history) == 0


@patch('huggingface_hub.HfApi')
def test_search_models(mock_hf_api):
    """Test searching for models."""
    mock_model = Mock()
    mock_model.modelId = "test/model"
    mock_model.downloads = 1000
    mock_model.likes = 50
    mock_model.tags = ["text-generation"]
    
    mock_api = Mock()
    mock_api.list_models.return_value = [mock_model]
    mock_hf_api.return_value = mock_api
    
    client = HuggingChatClient(token="test_token")
    models = client.search_models("test", limit=5)
    
    assert len(models) == 1
    assert models[0]['id'] == "test/model"
    assert models[0]['downloads'] == 1000
    assert models[0]['likes'] == 50


def test_create_huggingchat_agent():
    """Test creating a HuggingChat agent."""
    code = create_huggingchat_agent(
        agent_name="TestAgent",
        system_prompt="You are helpful",
        temperature=0.8
    )
    
    assert "class TestAgent" in code
    assert "You are helpful" in code
    assert "temperature=0.8" in code
    assert "HuggingChatClient" in code
    assert "import" in code


@patch('huggingface_hub.InferenceClient')
def test_chat_error_handling(mock_inference_client):
    """Test error handling in chat."""
    mock_client = Mock()
    mock_client.chat_completion.side_effect = Exception("API Error")
    mock_inference_client.return_value = mock_client
    
    client = HuggingChatClient(token="test_token")
    
    with pytest.raises(RuntimeError) as exc_info:
        client.chat("Hello", stream=False)
    
    assert "HuggingChat API error" in str(exc_info.value)


def test_chat_conversation_history():
    """Test that conversation history is maintained."""
    with patch('huggingface_hub.InferenceClient') as mock_inference:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Response"
        
        mock_client = Mock()
        mock_client.chat_completion.return_value = mock_response
        mock_inference.return_value = mock_client
        
        client = HuggingChatClient(token="test_token")
        
        # First message
        client.chat("First message", stream=False)
        assert len(client.conversation_history) == 2
        
        # Second message - should include history
        client.chat("Second message", stream=False)
        assert len(client.conversation_history) == 4
        
        # Verify the second call included history
        second_call_args = mock_client.chat_completion.call_args_list[1]
        messages = second_call_args[1]['messages']
        assert len(messages) >= 3  # history + new message


def test_custom_model():
    """Test using custom model."""
    client = HuggingChatClient(
        token="test_token",
        model="custom/model-id"
    )
    assert client.model == "custom/model-id"


def test_get_headers():
    """Test header generation."""
    client = HuggingChatClient(token="test_token")
    headers = client._get_headers()
    
    assert "Content-Type" in headers
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_token"


def test_get_headers_no_token():
    """Test headers without token."""
    client = HuggingChatClient()
    client.token = None
    headers = client._get_headers()
    
    assert "Content-Type" in headers
    assert "Authorization" not in headers
