import json
import os
import subprocess
import sys


def test_cli_help():
    result = subprocess.run([sys.executable, "-m", "llm_agent_builder.cli", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "LLM Agent Builder" in result.stdout


def test_cli_generate_agent(temp_output_dir):
    agent_name = "CLITestAgent"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_agent_builder.cli",
            "generate",
            "--name",
            agent_name,
            "--output",
            temp_output_dir,
            "--model",
            "claude-3-5-sonnet-20241022",
            "--prompt",
            "Test prompt",
            "--task",
            "Test task",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert f"Agent '{agent_name}' has been created" in result.stdout

    output_file = os.path.join(temp_output_dir, f"{agent_name.lower()}.py")
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        content = f.read()
        assert f"class {agent_name}:" in content
        assert "claude-3-5-sonnet-20241022" in content


def test_cli_list_agents(temp_output_dir):
    # First create an agent
    agent_name = "ListTestAgent"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_agent_builder.cli",
            "generate",
            "--name",
            agent_name,
            "--output",
            temp_output_dir,
            "--prompt",
            "Test",
            "--task",
            "Test",
        ],
        capture_output=True,
        text=True,
    )

    # Then list agents
    result = subprocess.run(
        [sys.executable, "-m", "llm_agent_builder.cli", "list", "--output", temp_output_dir],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert agent_name.lower() in result.stdout.lower()


def test_cli_batch_generate(temp_output_dir):
    # Create a batch config file
    config = [
        {
            "name": "BatchAgent1",
            "prompt": "Test prompt 1",
            "task": "Test task 1",
            "model": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
        },
        {
            "name": "BatchAgent2",
            "prompt": "Test prompt 2",
            "task": "Test task 2",
            "model": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
        },
    ]

    config_file = os.path.join(temp_output_dir, "batch_config.json")
    with open(config_file, "w") as f:
        json.dump(config, f)

    result = subprocess.run(
        [sys.executable, "-m", "llm_agent_builder.cli", "batch", config_file, "--output", temp_output_dir],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "BatchAgent1" in result.stdout
    assert "BatchAgent2" in result.stdout

    # Verify files were created
    assert os.path.exists(os.path.join(temp_output_dir, "batchagent1.py"))
    assert os.path.exists(os.path.join(temp_output_dir, "batchagent2.py"))


def test_cli_invalid_agent_name():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_agent_builder.cli",
            "generate",
            "--name",
            "Invalid Name!",
            "--prompt",
            "Test",
            "--task",
            "Test",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Error" in result.stdout or "Error" in result.stderr
