import os
from typing import Optional
from jinja2 import Environment, FileSystemLoader

class AgentBuilder:
    def __init__(self, template_path: Optional[str] = None):
        if template_path is None:
            template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.template = self.env.get_template('agent_template.py.j2')

    def build_agent(self, agent_name: str, prompt: str, example_task: str, model: str = "claude-3-5-sonnet-20241022") -> str:
        """
        Generates the Python code for a new agent.

        :param agent_name: The name of the agent class to be generated.
        :param prompt: The system prompt for the agent.
        :param example_task: An example task for the agent.
        :param model: The default Anthropic model to use.
        :return: The generated Python code as a string.
        """
        return self.template.render(
            agent_name=agent_name,
            prompt=prompt,
            example_task=example_task,
            model=model
        )
