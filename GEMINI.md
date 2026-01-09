
# LLMAgentBuilder Context

## Project Overview
**LLMAgentBuilder** is a Python application designed to scaffold and generate other LLM-based agents. It uses Jinja2 templates to create Python code for new agents that interact with the **Anthropic API (Claude)**. The system allows developers to define an agent's name, system prompt, and example tasks via CLI arguments, then automatically generates the corresponding Python class and script.

## Architecture
The project is structured as a Python package with a clear separation between the builder logic and the generated output.

*   **Core Logic (`llm_agent_builder/`):**
    *   `agent_builder.py`: Contains the `AgentBuilder` class, which manages the template environment and data context.
    *   `templates/`: Stores Jinja2 templates (e.g., `agent_template.py.j2`) defining the structure of generated agents (using the `anthropic` client).
*   **Execution:** `main.py` serves as the CLI entry point, parsing arguments and invoking the builder.
*   **Output:** Generated agents are saved to the `generated_agents/` directory.

## Key Files
*   `main.py`: CLI entry point. Parses arguments (`--name`, `--prompt`, etc.) and runs the builder.
*   `llm_agent_builder/agent_builder.py`: The main logic for rendering agent code.
*   `llm_agent_builder/templates/agent_template.py.j2`: The blueprint for new agents (Anthropic-based).
*   `setup.py`: Package installation configuration.
*   `test_with_mock_key.sh`: Shell script for testing the build process without a real API key.

## Building and Running

### Prerequisites
*   Python 3.8+
*   Anthropic API Key

### Installation
1.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
2.  Install dependencies:
    ```bash
    pip install -e .
    ```

### Usage
1.  **Configure Environment:**
    Set your Anthropic API key (required for the *generated* agents to run):
    ```bash
    export ANTHROPIC_API_KEY="sk-ant-..."
    ```
    Optionally set the model:
    ```bash
    export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
    ```

2.  **Generate an Agent:**
    Run the main script. You can use default settings or customize via CLI:
    ```bash
    # Default
    python main.py
    
    # Custom Agent
    python main.py --name "CodeReviewer" --prompt "You are a strict code reviewer." --task "Review this PR."
    ```

3.  **Run the Generated Agent:**
    Navigate to the output directory and run the generated script:
    ```bash
    python generated_agents/codereviewer.py
    ```

## Development Conventions
*   **Templating:** Uses Jinja2 for code generation. Changes to the agent structure should be made in `llm_agent_builder/templates/`.
*   **Dependency Management:** Dependencies (`anthropic`, `Jinja2`, `python-dotenv`) are listed in `requirements.txt`.
*   **Secrets:** API keys are managed via environment variables (`ANTHROPIC_API_KEY`) and are never hardcoded.