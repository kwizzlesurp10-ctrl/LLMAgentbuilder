import os
import argparse
import sys
import json
import subprocess
from typing import Optional, List
from pathlib import Path

# Add parent directory to path to allow running script directly
# This allows the script to be run as: python llm_agent_builder/cli.py
# or as: python -m llm_agent_builder.cli
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from llm_agent_builder.agent_builder import AgentBuilder
from dotenv import load_dotenv

def get_input(prompt: str, default: str, validator=None) -> str:
    """Get user input with optional validation."""
    while True:
        value = input(f"{prompt} [{default}]: ").strip()
        value = value if value else default
        if validator:
            try:
                validator(value)
                return value
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
                continue
        return value

def validate_agent_name(name: str) -> None:
    """Validate agent name."""
    if not name:
        raise ValueError("Agent name cannot be empty")
    if not name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("Agent name must be alphanumeric (with underscores or hyphens)")

def list_agents(output_dir: str = "generated_agents") -> None:
    """List all generated agents."""
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"Output directory '{output_dir}' does not exist.")
        return
    
    agents = list(output_path.glob("*.py"))
    if not agents:
        print(f"No agents found in '{output_dir}'.")
        return
    
    print(f"\nFound {len(agents)} agent(s) in '{output_dir}':")
    print("-" * 60)
    for agent_file in sorted(agents):
        print(f"  • {agent_file.stem}")
    print("-" * 60)

def test_agent(agent_path: str, task: Optional[str] = None) -> None:
    """Test a generated agent."""
    agent_file = Path(agent_path)
    if not agent_file.exists():
        print(f"Error: Agent file '{agent_path}' not found.")
        sys.exit(1)
    
    api_key = os.environ.get("GOOGLE_GEMINI_KEY") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not api_key:
        print("Error: API key not found. Please set GOOGLE_GEMINI_KEY or HUGGINGFACEHUB_API_TOKEN.")
        sys.exit(1)
    
    if not task:
        task = input("Enter task to test: ").strip()
        if not task:
            print("Error: Task cannot be empty.")
            sys.exit(1)
    
    try:
        cmd = [sys.executable, str(agent_file), "--task", task]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("Agent Execution Result:")
            print("=" * 60)
            print(result.stdout)
            if result.stderr:
                print("\nWarnings/Errors:")
                print(result.stderr)
        else:
            print(f"Error: Agent execution failed with code {result.returncode}")
            print(result.stderr)
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: Agent execution timed out after 60 seconds.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running agent: {e}")
        sys.exit(1)

def batch_generate(config_file: str, output_dir: str = "generated_agents", template: Optional[str] = None) -> None:
    """Generate multiple agents from a JSON configuration file."""
    config_path = Path(config_file)
    if not config_path.exists():
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            configs = json.load(f)
        
        if not isinstance(configs, list):
            print("Error: Configuration file must contain a JSON array of agent configurations.")
            sys.exit(1)
        
        builder = AgentBuilder(template_path=template)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"Generating {len(configs)} agent(s)...")
        print("-" * 60)
        
        for i, config in enumerate(configs, 1):
            try:
                agent_name = config.get("name", f"Agent{i}")
                prompt = config.get("prompt", "")
                task = config.get("task", "")
                model = config.get("model", "gemini-1.5-pro")
                provider = config.get("provider", "google")
                
                if not prompt or not task:
                    print(f"  [{i}] Skipping '{agent_name}': missing prompt or task")
                    continue
                
                agent_code = builder.build_agent(
                    agent_name=agent_name,
                    prompt=prompt,
                    example_task=task,
                    model=model,
                    provider=provider
                )
                
                agent_file = output_path / f"{agent_name.lower()}.py"
                with open(agent_file, "w") as f:
                    f.write(agent_code)
                
                print(f"  [{i}] ✓ Generated '{agent_name}' -> {agent_file}")
            except Exception as e:
                print(f"  [{i}] ✗ Error generating '{config.get('name', f'Agent{i}')}': {e}")
        
        print("-" * 60)
        print(f"Batch generation complete. Check '{output_dir}' for generated agents.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main() -> None:
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="LLM Agent Builder - Generate, test, and manage AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate an agent interactively
  llm-agent-builder generate

  # Generate with command-line arguments
  llm-agent-builder generate --name CodeReviewer --prompt "You are a code reviewer" --task "Review this code"

  # List all generated agents
  llm-agent-builder list

  # Test an agent
  llm-agent-builder test generated_agents/myagent.py --task "Review this function"

  # Batch generate from config file
  llm-agent-builder batch agents.json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate subcommand
    gen_parser = subparsers.add_parser("generate", help="Generate a new agent")
    gen_parser.add_argument("--name", default="MyAwesomeAgent", help="Name of the agent to be built")
    gen_parser.add_argument("--prompt", default="You are a helpful assistant that specializes in writing Python code.", help="System prompt for the agent")
    gen_parser.add_argument("--task", default="Write a Python function that calculates the factorial of a number.", help="Example task for the agent")
    gen_parser.add_argument("--output", default="generated_agents", help="Output directory for the generated agent")
    gen_parser.add_argument("--model", help="Model to use (overrides .env)")
    gen_parser.add_argument("--provider", default="google", choices=["google", "huggingface", "huggingchat"], help="LLM Provider to use")
    gen_parser.add_argument("--template", help="Path to a custom Jinja2 template file")
    gen_parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    gen_parser.add_argument("--db-path", help="Path to a SQLite database for the agent to use")
    
    # List subcommand
    list_parser = subparsers.add_parser("list", help="List all generated agents")
    list_parser.add_argument("--output", default="generated_agents", help="Output directory to search")
    
    # Test subcommand
    test_parser = subparsers.add_parser("test", help="Test a generated agent")
    test_parser.add_argument("agent_path", help="Path to the agent Python file")
    test_parser.add_argument("--task", help="Task to test the agent with")
    
    # Batch subcommand
    batch_parser = subparsers.add_parser("batch", help="Generate multiple agents from a JSON config file")
    batch_parser.add_argument("config_file", help="Path to JSON configuration file")
    batch_parser.add_argument("--output", default="generated_agents", help="Output directory for generated agents")
    batch_parser.add_argument("--template", help="Path to a custom Jinja2 template file")
    
    # Web subcommand
    web_parser = subparsers.add_parser("web", help="Launch the web interface")
    web_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    web_parser.add_argument("--port", type=int, default=7860, help="Port to bind to")
    
    args = parser.parse_args()
    
    # Handle no command (default to generate in interactive mode)
    # Handle no command (default to web interface)
    if not args.command:
        print("No command provided. Launching web interface...")
        args.command = "web"
        # Set default values for web command since they weren't parsed
        args.host = "0.0.0.0"
        args.port = 7860
    
    try:
        if args.command == "generate":
            # Interactive mode: triggered by --interactive flag or when no arguments provided
            # Check if user provided any arguments after the script name:
            # - len(sys.argv) == 1: no command provided (handled above, sets args.interactive=True)
            # - len(sys.argv) == 2: only "generate" command provided (no additional args)
            # - len(sys.argv) > 2: additional arguments provided (use command-line mode)
            # This check is robust and doesn't depend on args.interactive being set above
            no_args_provided = len(sys.argv) <= 2
            
            if args.interactive or no_args_provided:
                print("Starting interactive agent generation...")
                name = get_input("Agent Name", args.name, validator=validate_agent_name)
                prompt = get_input("System Prompt", args.prompt)
                task = get_input("Example Task", args.task)
                output = get_input("Output Directory", args.output)
                default_model = os.environ.get("GOOGLE_GEMINI_MODEL", "gemini-1.5-pro")
                model = get_input("Model", default_model)
                provider = get_input("Provider (google/huggingface/huggingchat)", args.provider)
                template = get_input("Custom Template Path (optional)", "")
                db_path = get_input("SQLite Database Path (optional)", "")
                
                # Validate provider
                if provider not in ["google", "huggingface", "huggingchat"]:
                    print(f"Error: Invalid provider '{provider}'. Must be 'google', 'huggingface', or 'huggingchat'.")
                    sys.exit(1)
            else:
                name = args.name
                prompt = args.prompt
                task = args.task
                output = args.output
                model = args.model
                provider = args.provider
                template = args.template
                db_path = args.db_path
            
            # Validate agent name
            try:
                validate_agent_name(name)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            
            # Override GOOGLE_GEMINI_MODEL if provided
            if model:
                os.environ["GOOGLE_GEMINI_MODEL"] = model
            
            # Create an instance of the AgentBuilder
            builder = AgentBuilder(template_path=template)
            
            # Generate the agent code
            default_model = model or ("gemini-1.5-pro" if provider == "google" else "meta-llama/Meta-Llama-3-8B-Instruct")
            agent_code = builder.build_agent(
                agent_name=name, 
                prompt=prompt, 
                example_task=task, 
                model=default_model,
                provider=provider,
                db_path=db_path if db_path else None
            )
            
            # Define the output path for the generated agent
            os.makedirs(output, exist_ok=True)
            output_path = os.path.join(output, f"{name.lower()}.py")
            
            # Write the generated code to a file
            with open(output_path, "w") as f:
                f.write(agent_code)
            
            print(f"\n✓ Agent '{name}' has been created and saved to '{output_path}'")
            print("To use the agent, you need to set the GOOGLE_GEMINI_KEY environment variable.")
            
        elif args.command == "list":
            list_agents(args.output)
            
        elif args.command == "test":
            test_agent(args.agent_path, args.task)
            
        elif args.command == "batch":
            batch_generate(args.config_file, args.output, args.template)
            
        elif args.command == "web":
            run_web_server(args.host, args.port)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def run_web_server(host: str, port: int) -> None:
    """Run the web interface server."""
    try:
        import uvicorn
        print(f"Starting web interface at http://{host}:{port}")
        uvicorn.run("server.main:app", host=host, port=port, reload=False)
    except ImportError:
        print("Error: uvicorn is not installed. Please install it with 'pip install uvicorn'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting web server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
