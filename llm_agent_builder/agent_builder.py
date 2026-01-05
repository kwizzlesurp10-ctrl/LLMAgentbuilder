import os
from typing import Optional, List, Dict, Any
from jinja2 import Environment, FileSystemLoader

class AgentBuilder:
    def __init__(self, template_path: Optional[str] = None):
        if template_path and os.path.isfile(template_path):
            template_dir = os.path.dirname(template_path)
            template_name = os.path.basename(template_path)
            self.env = Environment(loader=FileSystemLoader(template_dir))
            self.template = self.env.get_template(template_name)
        else:
            if template_path is None:
                template_path = os.path.join(os.path.dirname(__file__), 'templates')
            self.env = Environment(loader=FileSystemLoader(template_path))
            self.template = self.env.get_template('agent_template.py.j2')

    
    def build_agent(
        self,
        agent_name: str,
        prompt: str,
        example_task: str,
        model: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic",
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        enable_multi_step: bool = False,
        db_path: Optional[str] = None,
        agents: Optional[List[Dict[str, Any]]] = None,
        swarm_config: Optional[Dict[str, Any]] = None,
        docs_path: Optional[str] = None
    ) -> str:
        """
        Generates the Python code for a new agent or swarm.

        :param agent_name: The name of the agent class to be generated.
        :param prompt: The system prompt for the agent.
        :param example_task: An example task for the agent.
        :param model: The model to use.
        :param provider: The provider (anthropic or huggingface).
        :param stream: Whether to stream the response.
        :param tools: Optional list of tool definitions for tool calling support.
        :param enable_multi_step: Enable multi-step workflow capabilities.
        :param db_path: Optional path to a SQLite database.
        :param agents: List of agents for swarm generation.
        :param swarm_config: Configuration for swarm generation.
        :param docs_path: Optional path to a directory of documents for RAG.
        :return: The generated Python code as a string.
        """

        if swarm_config:
            template = self.env.get_template("swarm_template.py.j2")
            return template.render(
                swarm_name=agent_name,
                strategy=swarm_config.get("strategy", "round_robin"),
                agents=agents or [],
                example_task=example_task
            )

        if provider == "huggingface":
            template_name = "agent_template_hf.py.j2"
        elif provider == "openai":
            template_name = "agent_template_openai.py.j2"
        elif provider == "anytool":
            template_name = "agent_template_anytool.py.j2"
        else:
            if provider == "swarm":  # Fallback if specific provider name used
                template_name = "swarm_template.py.j2"
                return self.env.get_template(template_name).render(
                    swarm_name=agent_name,
                    strategy=swarm_config.get("strategy", "round_robin") if swarm_config else "round_robin",
                    agents=agents or [],
                    example_task=example_task
                )
            template_name = "agent_template.py.j2"

        template = self.env.get_template(template_name)

        # Process tools to inject implementations
        tool_implementations = []
        if tools:
            from llm_agent_builder.tool_library import ToolLibrary
            for tool in tools:
                # Check if it's a standard tool (has a name in the library)
                # and doesn't define its own custom implementation (we assume custom schema implies custom tool for now, 
                # but let's strictly check if the name matches a library tool)
                std_tool = ToolLibrary.get_tool(tool["name"])
                if std_tool:
                    # If the input schema matches (or is close enough), use the standard implementation
                    # For simplicity, we just check name match for now.
                    tool_implementations.append(std_tool.implementation)

        return template.render(
            agent_name=agent_name,
            prompt=prompt,
            example_task=example_task,
            model=model,
            provider=provider,
            stream=stream,
            tools=tools or [],
            tool_implementations=tool_implementations,
            enable_multi_step=enable_multi_step,
            db_path=db_path,
            docs_path=docs_path
        )
