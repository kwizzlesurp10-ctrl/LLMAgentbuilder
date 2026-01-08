import sys
from pathlib import Path

import pytest

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_GEMINI_KEY", "mock-api-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "mock-model")


@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "generated_agents"
    output_dir.mkdir()
    return str(output_dir)
