---
title: LLM Agent Builder
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---
# LLM Agent Builder

This project is a PyCharm application that contains an LLM agent capable of building other LLM agents.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Create and activate a virtual environment (recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. Install the package in development mode:

    ```bash
    pip install -e .
    ```

    Or install dependencies directly:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your Anthropic API key as an environment variable:

    **For Testing (Mock Key):**

    ```bash
    export ANTHROPIC_API_KEY="sk-ant-test-mock-key-for-testing-purposes-1234567890abcdef"
    ```

    **For Production (Real Key):**

    ```bash
    export ANTHROPIC_API_KEY="your-actual-api-key-here"
    ```

    > **Note:** The mock key above is for testing code structure only. It will not work for actual API calls. Replace it with your real Anthropic API key for production use.

    You can also configure the model by setting the `ANTHROPIC_MODEL` environment variable in your `.env` file.
    Available models include:
    - `claude-3-5-sonnet-20241022` (Default)
    - `claude-3-opus-20240229`
    - `claude-3-sonnet-20240229`
    - `claude-3-haiku-20240307`

4. Run the `main.py` script to generate a new agent:

    **Basic Usage:**

    ```bash
    python main.py
    ```

## Web Interface (New!)

You can also use the modern web interface to generate agents.

### Prerequisites

- Node.js installed
- Python dependencies installed (`pip install -r requirements.txt`)

### Running the Web App

1. **Start the Backend Server:**

    ```bash
    uvicorn server.main:app --reload
    ```

    The API will be available at `http://localhost:8000`.

2. **Start the Frontend:**
    Open a new terminal:

    ```bash
    cd frontend
    npm run dev
    ```

    Open your browser to `http://localhost:5173`.

## Deployment (Hugging Face Spaces)

This project is configured for deployment to Hugging Face Spaces using Docker.

1. Create a new Space on Hugging Face.
2. Select **Docker** as the SDK.
3. Push the entire repository to the Space.
    - The `Dockerfile` will automatically build the React frontend and serve it via the FastAPI backend.
    - The application is stateless: generated agents will be downloaded to your local machine.

    **Advanced Usage (CLI):**
    You can customize the agent generation using command-line arguments:

    ```bash
    llm-agent-builder --name "DataAnalyst" \
                      --prompt "You are a data analyst expert in Pandas." \
                      --task "Analyze this CSV file and provide summary statistics." \
                      --model "claude-3-opus-20240229"
    ```

    **Interactive Mode:**
    If you run the command without arguments, it will launch in interactive mode:

    ```bash
    llm-agent-builder
    ```

    **Available Arguments:**
    - `--name`: Name of the agent (default: "MyAwesomeAgent")
    - `--prompt`: System prompt for the agent
    - `--task`: Example task for the agent
    - `--output`: Output directory (default: "generated_agents")
    - `--model`: Anthropic model to use (overrides `.env`)
    - `--interactive`: Force interactive mode

## Development

### Testing

Run unit tests using `pytest`:

```bash
pytest
```

### Type Checking

Run static type checking using `mypy`:

```bash
mypy llm_agent_builder
```

### CI/CD

This project uses GitHub Actions for Continuous Integration. Tests are automatically run on every push and pull request to the `main` branch.

## Project Structure

- `llm_agent_builder/` - Main package containing the agent builder
  - `agent_builder.py` - Core AgentBuilder class
  - `cli.py` - Command-line interface logic
  - `templates/` - Jinja2 templates for agent generation
- `main.py` - Entry point script (calls `cli.main`)
- `test_with_mock_key.sh` - Test script using mock API key for testing
- `.env.example` - Example environment file with mock API key
- `generated_agents/` - Output directory for generated agents (created automatically)
- `tests/` - Unit tests
