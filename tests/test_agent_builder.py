import pytest
from llm_agent_builder.agent_builder import AgentBuilder

def test_agent_builder_initialization():
    builder = AgentBuilder()
    assert builder.env is not None
    assert builder.template is not None

def test_build_agent_content():
    builder = AgentBuilder()
    agent_name = "TestAgent"
    prompt = "Test Prompt"
    example_task = "Test Task"
    model = "claude-3-test"
    
    # Test with Anthropic provider since the test expects Anthropic code
    code = builder.build_agent(agent_name, prompt, example_task, model=model, provider="anthropic")
    
    assert f"class {agent_name}:" in code
    assert f'self.prompt = "{prompt}"' in code
    assert f'model=os.environ.get("ANTHROPIC_MODEL", "{model}")' in code
    assert "import anthropic" in code
