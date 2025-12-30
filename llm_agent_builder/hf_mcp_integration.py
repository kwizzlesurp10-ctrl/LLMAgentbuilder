"""
HuggingFace MCP (Model Context Protocol) Integration

This module provides integration with HuggingFace's Model Context Protocol,
enabling seamless interaction with HuggingFace models, datasets, and spaces
through a standardized protocol.
"""

import os
import json
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from huggingface_hub import (
    HfApi,
    InferenceClient,
    ModelCard,
    DatasetCard,
    SpaceCard,
    list_models,
    list_datasets,
    list_spaces,
)


class MCPResourceType(str, Enum):
    """Resource types supported by HuggingFace MCP."""
    MODEL = "model"
    DATASET = "dataset"
    SPACE = "space"
    INFERENCE = "inference"


@dataclass
class MCPResource:
    """Represents a resource in the HuggingFace MCP."""
    uri: str
    name: str
    resource_type: MCPResourceType
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class MCPTool:
    """Represents a tool available through HuggingFace MCP."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class HuggingFaceMCPClient:
    """
    Client for interacting with HuggingFace through Model Context Protocol.
    
    This client provides a standardized way to access HuggingFace resources
    including models, datasets, spaces, and inference capabilities.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize HuggingFace MCP client.
        
        :param token: HuggingFace API token
        """
        self.token = token or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        self.api = HfApi(token=self.token)
        self.inference_client = InferenceClient(token=self.token)
        
    def get_available_tools(self) -> List[MCPTool]:
        """
        Get list of available tools through the MCP interface.
        
        :return: List of available tools
        """
        tools = [
            MCPTool(
                name="search_models",
                description="Search for models on HuggingFace Hub",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "task": {"type": "string", "description": "Filter by task"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="search_datasets",
                description="Search for datasets on HuggingFace Hub",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="get_model_info",
                description="Get detailed information about a model",
                input_schema={
                    "type": "object",
                    "properties": {
                        "model_id": {"type": "string", "description": "Model ID"}
                    },
                    "required": ["model_id"]
                }
            ),
            MCPTool(
                name="inference",
                description="Run inference on a model",
                input_schema={
                    "type": "object",
                    "properties": {
                        "model_id": {"type": "string", "description": "Model ID"},
                        "inputs": {"type": "string", "description": "Input text"},
                        "parameters": {"type": "object", "description": "Model parameters"}
                    },
                    "required": ["model_id", "inputs"]
                }
            ),
            MCPTool(
                name="get_model_safety",
                description="Get safety and content moderation info for a model",
                input_schema={
                    "type": "object",
                    "properties": {
                        "model_id": {"type": "string", "description": "Model ID"}
                    },
                    "required": ["model_id"]
                }
            ),
            MCPTool(
                name="search_spaces",
                description="Search for Spaces on HuggingFace Hub",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            )
        ]
        return tools
    
    def get_resources(
        self,
        resource_type: Optional[MCPResourceType] = None,
        limit: int = 10
    ) -> List[MCPResource]:
        """
        Get available resources from HuggingFace.
        
        :param resource_type: Filter by resource type
        :param limit: Maximum number of resources to return
        :return: List of resources
        """
        resources = []
        
        if resource_type is None or resource_type == MCPResourceType.MODEL:
            models = list_models(limit=limit, sort="downloads", direction=-1)
            for model in models:
                resources.append(MCPResource(
                    uri=f"hf://models/{model.modelId}",
                    name=model.modelId,
                    resource_type=MCPResourceType.MODEL,
                    description=f"Model with {getattr(model, 'downloads', 0)} downloads",
                    metadata={
                        "downloads": getattr(model, 'downloads', 0),
                        "likes": getattr(model, 'likes', 0),
                        "tags": getattr(model, 'tags', [])
                    }
                ))
        
        if resource_type is None or resource_type == MCPResourceType.DATASET:
            datasets = list_datasets(limit=limit, sort="downloads", direction=-1)
            for dataset in datasets:
                resources.append(MCPResource(
                    uri=f"hf://datasets/{dataset.id}",
                    name=dataset.id,
                    resource_type=MCPResourceType.DATASET,
                    description=f"Dataset with {getattr(dataset, 'downloads', 0)} downloads",
                    metadata={
                        "downloads": getattr(dataset, 'downloads', 0)
                    }
                ))
        
        if resource_type is None or resource_type == MCPResourceType.SPACE:
            spaces = list_spaces(limit=limit, sort="likes", direction=-1)
            for space in spaces:
                resources.append(MCPResource(
                    uri=f"hf://spaces/{space.id}",
                    name=space.id,
                    resource_type=MCPResourceType.SPACE,
                    description=f"Space with {getattr(space, 'likes', 0)} likes",
                    metadata={
                        "likes": getattr(space, 'likes', 0),
                        "sdk": getattr(space, 'sdk', None)
                    }
                ))
        
        return resources
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool through the MCP interface.
        
        :param tool_name: Name of the tool to call
        :param arguments: Arguments for the tool
        :return: Tool execution result
        """
        if tool_name == "search_models":
            return self._search_models(**arguments)
        elif tool_name == "search_datasets":
            return self._search_datasets(**arguments)
        elif tool_name == "get_model_info":
            return self._get_model_info(**arguments)
        elif tool_name == "inference":
            return self._run_inference(**arguments)
        elif tool_name == "get_model_safety":
            return self._get_model_safety(**arguments)
        elif tool_name == "search_spaces":
            return self._search_spaces(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _search_models(
        self,
        query: str,
        task: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search for models."""
        models = list_models(
            search=query,
            task=task,
            limit=limit,
            sort="downloads",
            direction=-1
        )
        
        results = []
        for model in models:
            results.append({
                "id": model.modelId,
                "downloads": getattr(model, 'downloads', 0),
                "likes": getattr(model, 'likes', 0),
                "tags": getattr(model, 'tags', []),
                "pipeline_tag": getattr(model, 'pipeline_tag', None)
            })
        
        return {
            "results": results,
            "count": len(results)
        }
    
    def _search_datasets(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for datasets."""
        datasets = list_datasets(
            search=query,
            limit=limit,
            sort="downloads",
            direction=-1
        )
        
        results = [
            {
                "id": dataset.id,
                "downloads": getattr(dataset, 'downloads', 0),
                "likes": getattr(dataset, 'likes', 0)
            }
            for dataset in datasets
        ]
        
        return {
            "results": results,
            "count": len(results)
        }
    
    def _search_spaces(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for Spaces."""
        spaces = list_spaces(
            search=query,
            limit=limit,
            sort="likes",
            direction=-1
        )
        
        results = [
            {
                "id": space.id,
                "likes": getattr(space, 'likes', 0),
                "sdk": getattr(space, 'sdk', None)
            }
            for space in spaces
        ]
        
        return {
            "results": results,
            "count": len(results)
        }
    
    def _get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get detailed model information."""
        try:
            model_info = self.api.model_info(model_id)
            
            # Try to load model card (may fail for some models)
            card_data = None
            card_text = None
            try:
                card = ModelCard.load(model_id)
                card_data = card.data.to_dict() if card.data else None
                card_text = card.text[:500] if card.text else None  # First 500 chars
            except Exception:
                # Model card not available or failed to load
                pass
            
            return {
                "id": model_id,
                "author": getattr(model_info, 'author', None),
                "downloads": getattr(model_info, 'downloads', 0),
                "likes": getattr(model_info, 'likes', 0),
                "tags": getattr(model_info, 'tags', []),
                "pipeline_tag": getattr(model_info, 'pipeline_tag', None),
                "gated": getattr(model_info, 'gated', False),
                "library_name": getattr(model_info, 'library_name', None),
                "card_data": card_data,
                "card_text": card_text
            }
        except Exception as e:
            return {"error": str(e), "model_id": model_id}
    
    def _get_model_safety(self, model_id: str) -> Dict[str, Any]:
        """Get model safety information."""
        try:
            model_info = self.api.model_info(model_id)
            tags = getattr(model_info, 'tags', [])
            
            safety_tags = [
                tag for tag in tags
                if any(keyword in tag.lower() for keyword in [
                    'safety', 'moderation', 'toxicity', 'bias', 'ethical'
                ])
            ]
            
            return {
                "model_id": model_id,
                "gated": getattr(model_info, 'gated', False),
                "safety_tags": safety_tags,
                "has_safety_features": len(safety_tags) > 0,
                "license": getattr(model_info, 'cardData', {}).get('license', 'Unknown'),
                "all_tags": tags
            }
        except Exception as e:
            return {"error": str(e), "model_id": model_id}
    
    def _run_inference(
        self,
        model_id: str,
        inputs: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run inference on a model."""
        try:
            result = self.inference_client.post(
                json={
                    "inputs": inputs,
                    "parameters": parameters or {}
                },
                model=model_id
            )
            return {
                "model_id": model_id,
                "output": result,
                "success": True
            }
        except Exception as e:
            return {
                "model_id": model_id,
                "error": str(e),
                "success": False
            }
    
    def export_mcp_config(self, output_path: str = "hf_mcp_config.json") -> None:
        """
        Export MCP configuration for HuggingFace integration.
        
        :param output_path: Path to save the configuration
        """
        config = {
            "name": "huggingface",
            "version": "1.0.0",
            "description": "HuggingFace Model Context Protocol Integration",
            "tools": [tool.to_dict() for tool in self.get_available_tools()],
            "resources": {
                "models": "hf://models/*",
                "datasets": "hf://datasets/*",
                "spaces": "hf://spaces/*"
            },
            "authentication": {
                "type": "bearer_token",
                "env_var": "HUGGINGFACEHUB_API_TOKEN"
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"MCP configuration exported to {output_path}")


def create_mcp_agent_template() -> str:
    """
    Create an agent template that uses HuggingFace MCP integration.
    
    :return: Python code for MCP-enabled agent
    """
    template = '''"""
MCP-Enabled HuggingFace Agent
Generated by LLM Agent Builder with MCP Integration
"""

import os
from typing import Optional, Dict, Any
from llm_agent_builder.hf_mcp_integration import HuggingFaceMCPClient


class MCPHuggingFaceAgent:
    """Agent that uses HuggingFace MCP for enhanced capabilities."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize MCP-enabled agent.
        
        :param token: HuggingFace API token
        """
        self.mcp_client = HuggingFaceMCPClient(token=token)
        self.available_tools = self.mcp_client.get_available_tools()
        
    def search_and_analyze_models(self, query: str, task: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for models and get detailed safety information.
        
        :param query: Search query
        :param task: Optional task filter
        :return: Search results with safety analysis
        """
        # Search models
        search_result = self.mcp_client.call_tool(
            "search_models",
            {"query": query, "task": task, "limit": 5}
        )
        
        # Get safety info for top models
        models_with_safety = []
        for model in search_result.get("results", []):
            safety_info = self.mcp_client.call_tool(
                "get_model_safety",
                {"model_id": model["id"]}
            )
            models_with_safety.append({
                **model,
                "safety": safety_info
            })
        
        return {
            "query": query,
            "models": models_with_safety,
            "count": len(models_with_safety)
        }
    
    def run_inference_safely(
        self,
        model_id: str,
        inputs: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run inference with safety checks.
        
        :param model_id: Model ID
        :param inputs: Input text
        :param parameters: Model parameters
        :return: Inference result with safety information
        """
        # Check model safety first
        safety_info = self.mcp_client.call_tool(
            "get_model_safety",
            {"model_id": model_id}
        )
        
        if not safety_info.get("has_safety_features"):
            print(f"Warning: Model {model_id} may not have safety features enabled")
        
        # Run inference
        result = self.mcp_client.call_tool(
            "inference",
            {
                "model_id": model_id,
                "inputs": inputs,
                "parameters": parameters
            }
        )
        
        return {
            "result": result,
            "safety_info": safety_info
        }
    
    def list_available_tools(self) -> None:
        """Print available MCP tools."""
        print("Available MCP Tools:")
        print("-" * 60)
        for tool in self.available_tools:
            print(f"  • {tool.name}: {tool.description}")
        print("-" * 60)


if __name__ == '__main__':
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="MCP-enabled HuggingFace Agent")
    parser.add_argument("--search", help="Search for models")
    parser.add_argument("--task", help="Filter by task")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    args = parser.parse_args()
    
    agent = MCPHuggingFaceAgent()
    
    if args.list_tools:
        agent.list_available_tools()
    elif args.search:
        results = agent.search_and_analyze_models(args.search, args.task)
        print(f"\\nFound {results['count']} models for query '{results['query']}':")
        for model in results["models"]:
            print(f"\\n  {model['id']}")
            print(f"    Downloads: {model['downloads']}")
            print(f"    Safety Features: {model['safety'].get('has_safety_features', False)}")
            print(f"    License: {model['safety'].get('license', 'Unknown')}")
    else:
        print("No action specified. Use --help for options.")
'''
    return template


if __name__ == "__main__":
    # Example usage
    client = HuggingFaceMCPClient()
    
    print("HuggingFace MCP Integration Test")
    print("=" * 60)
    
    # List available tools
    tools = client.get_available_tools()
    print(f"\nAvailable Tools: {len(tools)}")
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")
    
    # Export MCP configuration
    client.export_mcp_config()
    print("\nMCP configuration exported successfully!")
