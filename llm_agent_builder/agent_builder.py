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
        db_path: Optional[str] = None
    ) -> str:
        """
        Generates the Python code for a new agent.

        :param agent_name: The name of the agent class to be generated.
        :param prompt: The system prompt for the agent.
        :param example_task: An example task for the agent.
        :param model: The model to use.
        :param provider: The provider (anthropic or huggingface).
        :param stream: Whether to stream the response.
        :param tools: Optional list of tool definitions for tool calling support.
        :param enable_multi_step: Enable multi-step workflow capabilities.
        :param db_path: Optional path to a SQLite database.
        :return: The generated Python code as a string.
        """
        
        return self.template.render(
            agent_name=agent_name,
            prompt=prompt,
            example_task=example_task,
            model=model,
            provider=provider,
            stream=stream,
            tools=tools or [],
            enable_multi_step=enable_multi_step,
            db_path=db_path
        )
