"""
Tests for HuggingFace MCP integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from llm_agent_builder.hf_mcp_integration import (
    HuggingFaceMCPClient,
    MCPResource,
    MCPTool,
    MCPResourceType,
    create_mcp_agent_template
)


def test_mcp_resource():
    """Test MCPResource dataclass."""
    resource = MCPResource(
        uri="hf://models/test-model",
        name="test-model",
        resource_type=MCPResourceType.MODEL,
        description="Test model",
        metadata={"downloads": 1000}
    )
    
    assert resource.uri == "hf://models/test-model"
    assert resource.name == "test-model"
    assert resource.resource_type == MCPResourceType.MODEL
    
    # Test to_dict
    resource_dict = resource.to_dict()
    assert resource_dict['uri'] == "hf://models/test-model"
    assert resource_dict['metadata']['downloads'] == 1000


def test_mcp_tool():
    """Test MCPTool dataclass."""
    tool = MCPTool(
        name="test_tool",
        description="Test tool description",
        input_schema={"type": "object", "properties": {}}
    )
    
    assert tool.name == "test_tool"
    assert tool.description == "Test tool description"
    
    # Test to_dict
    tool_dict = tool.to_dict()
    assert tool_dict['name'] == "test_tool"


def test_mcp_client_init():
    """Test MCP client initialization."""
    with patch.dict('os.environ', {'HUGGINGFACEHUB_API_TOKEN': 'test_token'}):
        client = HuggingFaceMCPClient()
        assert client.token == "test_token"


@patch('llm_agent_builder.hf_mcp_integration.HfApi')
@patch('llm_agent_builder.hf_mcp_integration.InferenceClient')
def test_get_available_tools(mock_inference, mock_hf_api):
    """Test getting available tools."""
    client = HuggingFaceMCPClient(token="test_token")
    tools = client.get_available_tools()
    
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    # Check for expected tools
    tool_names = [tool.name for tool in tools]
    assert "search_models" in tool_names
    assert "search_datasets" in tool_names
    assert "get_model_info" in tool_names
    assert "inference" in tool_names
    assert "get_model_safety" in tool_names


@patch('llm_agent_builder.hf_mcp_integration.list_models')
def test_get_resources_models(mock_list_models):
    """Test getting model resources."""
    mock_model = Mock()
    mock_model.modelId = "test/model"
    mock_model.downloads = 1000
    mock_model.likes = 50
    mock_model.tags = ["text-generation"]
    
    mock_list_models.return_value = [mock_model]
    
    client = HuggingFaceMCPClient(token="test_token")
    resources = client.get_resources(
        resource_type=MCPResourceType.MODEL,
        limit=10
    )
    
    assert len(resources) == 1
    assert resources[0].name == "test/model"
    assert resources[0].resource_type == MCPResourceType.MODEL
    assert resources[0].metadata['downloads'] == 1000


@patch('llm_agent_builder.hf_mcp_integration.list_models')
def test_search_models_tool(mock_list_models):
    """Test search_models tool call."""
    mock_model = Mock()
    mock_model.modelId = "test/model"
    mock_model.downloads = 1000
    mock_model.likes = 50
    mock_model.tags = ["text-generation"]
    mock_model.pipeline_tag = "text-generation"
    
    mock_list_models.return_value = [mock_model]
    
    client = HuggingFaceMCPClient(token="test_token")
    result = client.call_tool("search_models", {
        "query": "test",
        "limit": 5
    })
    
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == "test/model"
    assert result["count"] == 1


@patch('llm_agent_builder.hf_mcp_integration.HfApi')
def test_get_model_info_tool(mock_hf_api):
    """Test get_model_info tool call."""
    mock_model_info = Mock()
    mock_model_info.author = "test-author"
    mock_model_info.downloads = 5000
    mock_model_info.likes = 100
    mock_model_info.tags = ["text-generation", "pytorch"]
    mock_model_info.pipeline_tag = "text-generation"
    mock_model_info.gated = False
    mock_model_info.library_name = "transformers"
    
    mock_card = Mock()
    mock_card.data = Mock()
    mock_card.data.to_dict.return_value = {"license": "MIT"}
    mock_card.text = "Model card text"
    
    mock_api_instance = Mock()
    mock_api_instance.model_info.return_value = mock_model_info
    mock_hf_api.return_value = mock_api_instance
    
    with patch('llm_agent_builder.hf_mcp_integration.ModelCard.load', return_value=mock_card):
        client = HuggingFaceMCPClient(token="test_token")
        result = client.call_tool("get_model_info", {"model_id": "test/model"})
    
    assert result["id"] == "test/model"
    assert result["author"] == "test-author"
    assert result["downloads"] == 5000
    assert result["gated"] is False


@patch('llm_agent_builder.hf_mcp_integration.HfApi')
def test_get_model_safety_tool(mock_hf_api):
    """Test get_model_safety tool call."""
    mock_model_info = Mock()
    mock_model_info.tags = ["safety", "moderation", "text-generation"]
    mock_model_info.gated = True
    mock_model_info.cardData = {"license": "Apache-2.0"}
    
    mock_api_instance = Mock()
    mock_api_instance.model_info.return_value = mock_model_info
    mock_hf_api.return_value = mock_api_instance
    
    client = HuggingFaceMCPClient(token="test_token")
    result = client.call_tool("get_model_safety", {"model_id": "test/model"})
    
    assert result["model_id"] == "test/model"
    assert result["gated"] is True
    assert result["has_safety_features"] is True
    assert "safety" in result["safety_tags"]


@patch('llm_agent_builder.hf_mcp_integration.InferenceClient')
def test_inference_tool(mock_inference_client):
    """Test inference tool call."""
    mock_response = {"generated_text": "Test output"}
    
    mock_client = Mock()
    mock_client.post.return_value = mock_response
    mock_inference_client.return_value = mock_client
    
    client = HuggingFaceMCPClient(token="test_token")
    result = client.call_tool("inference", {
        "model_id": "test/model",
        "inputs": "Test input"
    })
    
    assert result["success"] is True
    assert result["model_id"] == "test/model"
    assert result["output"] == mock_response


def test_call_tool_unknown():
    """Test calling unknown tool."""
    client = HuggingFaceMCPClient(token="test_token")
    
    with pytest.raises(ValueError) as exc_info:
        client.call_tool("unknown_tool", {})
    
    assert "Unknown tool" in str(exc_info.value)


def test_export_mcp_config(tmp_path):
    """Test exporting MCP configuration."""
    client = HuggingFaceMCPClient(token="test_token")
    
    output_file = tmp_path / "test_config.json"
    client.export_mcp_config(str(output_file))
    
    assert output_file.exists()
    
    # Read and verify config
    import json
    with open(output_file) as f:
        config = json.load(f)
    
    assert config["name"] == "huggingface"
    assert "tools" in config
    assert len(config["tools"]) > 0
    assert "resources" in config


def test_create_mcp_agent_template():
    """Test creating MCP agent template."""
    code = create_mcp_agent_template()
    
    assert isinstance(code, str)
    assert "MCPHuggingFaceAgent" in code
    assert "HuggingFaceMCPClient" in code
    assert "search_and_analyze_models" in code
    assert "run_inference_safely" in code


@patch('llm_agent_builder.hf_mcp_integration.list_datasets')
def test_search_datasets_tool(mock_list_datasets):
    """Test search_datasets tool call."""
    mock_dataset = Mock()
    mock_dataset.id = "test/dataset"
    mock_dataset.downloads = 500
    mock_dataset.likes = 25
    
    mock_list_datasets.return_value = [mock_dataset]
    
    client = HuggingFaceMCPClient(token="test_token")
    result = client.call_tool("search_datasets", {
        "query": "test",
        "limit": 5
    })
    
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == "test/dataset"


@patch('llm_agent_builder.hf_mcp_integration.list_spaces')
def test_search_spaces_tool(mock_list_spaces):
    """Test search_spaces tool call."""
    mock_space = Mock()
    mock_space.id = "test/space"
    mock_space.likes = 30
    mock_space.sdk = "gradio"
    
    mock_list_spaces.return_value = [mock_space]
    
    client = HuggingFaceMCPClient(token="test_token")
    result = client.call_tool("search_spaces", {
        "query": "test",
        "limit": 5
    })
    
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == "test/space"
    assert result["results"][0]["sdk"] == "gradio"


@patch('llm_agent_builder.hf_mcp_integration.InferenceClient')
def test_inference_tool_error(mock_inference_client):
    """Test inference tool with error."""
    mock_client = Mock()
    mock_client.post.side_effect = Exception("API Error")
    mock_inference_client.return_value = mock_client
    
    client = HuggingFaceMCPClient(token="test_token")
    result = client.call_tool("inference", {
        "model_id": "test/model",
        "inputs": "Test input"
    })
    
    assert result["success"] is False
    assert "error" in result
