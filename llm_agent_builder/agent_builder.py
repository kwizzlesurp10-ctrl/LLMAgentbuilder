import os
from typing import Optional
from jinja2 import Environment, FileSystemLoader

class AgentBuilder:
    def __init__(self, template_path: Optional[str] = None):
        if template_path is None:
            template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.template = self.env.get_template('agent_template.py.j2')

    def build_agent(self, agent_name: str, prompt: str, example_task: str, model: str = "claude-3-5-sonnet-20241022", provider: str = "anthropic", stream: bool = False) -> str:
        """
        Generates the Python code for a new agent.

        :param agent_name: The name of the agent class to be generated.
        :param prompt: The system prompt for the agent.
        :param example_task: An example task for the agent.
        :param model: The model to use.
        :param provider: The provider (anthropic or huggingface).
        :param stream: Whether to stream the response.
        :return: The generated Python code as a string.
        """
        template_name = 'agent_template_hf.py.j2' if provider == 'huggingface' else 'agent_template.py.j2'
        template = self.env.get_template(template_name)
        
        return template.render(
            agent_name=agent_name,
            prompt=prompt,
            example_task=example_task,
            model=model,
            stream=stream
        )
