from llm_agent_builder.agent_builder import AgentBuilder


def test_agent_builder_initialization():
    builder = AgentBuilder()
    assert builder.env is not None
    assert builder._template_cache is not None
    assert isinstance(builder._template_cache, dict)


def test_build_agent_content():
    builder = AgentBuilder()
    agent_name = "TestAgent"
    prompt = "Test Prompt"
    example_task = "Test Task"
    model = "gemini-1.5-pro"
    provider = "google"
    
    code = builder.build_agent(agent_name, prompt, example_task, model=model, provider="anthropic")
    
    assert f"class {agent_name}:" in code
    assert f'self.prompt = "{prompt}"' in code
    assert f'model_name = os.environ.get("GOOGLE_GEMINI_MODEL", "{model}")' in code
    assert "import google.generativeai as genai" in code

def test_template_caching():
    """Test that templates are cached for performance."""
    builder = AgentBuilder()
    
    # Build first agent - this should cache the template
    code1 = builder.build_agent("Agent1", "prompt1", "task1", provider="google")
    assert len(builder._template_cache) == 1
    
    # Build second agent with same provider - should reuse cached template
    code2 = builder.build_agent("Agent2", "prompt2", "task2", provider="google")
    assert len(builder._template_cache) == 1
    
    # Build agent with different provider - should cache new template
    code3 = builder.build_agent("Agent3", "prompt3", "task3", provider="huggingface")
    assert len(builder._template_cache) == 2
