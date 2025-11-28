import pytest
import os
import shutil

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "mock-api-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "mock-model")

@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "generated_agents"
    output_dir.mkdir()
    return str(output_dir)
