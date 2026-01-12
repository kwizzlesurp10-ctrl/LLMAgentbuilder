import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Pre-compile regex patterns for better performance
_AGENT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

# Add parent directory to path to allow running script directly
# This allows the script to be run as: python llm_agent_builder/cli.py
# or as: python -m llm_agent_builder.cli
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv

from llm_agent_builder.agent_builder import AgentBuilder


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
    if not _AGENT_NAME_PATTERN.match(name):
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
    
    # Use ConfigManager to get API key
    config_manager = get_config_manager()
    api_key = config_manager.get_any_api_key()
    
    if not api_key:
        print("Error: No API key found. Please configure at least one provider:")
        status = config_manager.get_configuration_status()
        for provider_name, info in status.items():
            print(f"  - {info['name']}: Set {info['env_var']}")
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
        with open(config_path, "r") as f:
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
                    agent_name=agent_name, prompt=prompt, example_task=task, model=model, provider=provider
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

def handle_config_command(args) -> None:
    """Handle configuration management commands."""
    from llm_agent_builder.config import get_config_manager, load_config
    
    if not hasattr(args, 'config_action') or not args.config_action:
        print("Error: No configuration action specified.")
        print("Available actions: show, validate, generate")
        sys.exit(1)
    
    try:
        if args.config_action == "show":
            # Show current configuration
            config_manager = get_config_manager()
            
            if args.format == "yaml":
                print(config_manager.to_yaml())
            else:
                print(config_manager.to_json())
        
        elif args.config_action == "validate":
            # Validate a configuration file
            config_manager = get_config_manager()
            is_valid, error = config_manager.validate_config_file(args.file)
            
            if is_valid:
                print(f"✓ Configuration file '{args.file}' is valid.")
            else:
                print(f"✗ Configuration file '{args.file}' is invalid:")
                print(f"  {error}")
                sys.exit(1)
        
        elif args.config_action == "generate":
            # Generate a default configuration file
            config = load_config()
            
            output_path = Path(args.output)
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.format == "yaml":
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)
            else:
                with open(output_path, 'w') as f:
                    json.dump(config.model_dump(), f, indent=2)
            
            print(f"✓ Generated configuration file: {output_path}")
    
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
  
  # Configuration management
  llm-agent-builder config show
  llm-agent-builder config validate --file config/production.yaml
  llm-agent-builder config generate
        """
    )
    
    # Global arguments
    parser.add_argument("--config", help="Path to configuration file", dest="config_file")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate subcommand
    gen_parser = subparsers.add_parser("generate", help="Generate a new agent")
    gen_parser.add_argument("--name", default="MyAwesomeAgent", help="Name of the agent to be built")
    gen_parser.add_argument(
        "--prompt",
        default="You are a helpful assistant that specializes in writing Python code.",
        help="System prompt for the agent",
    )
    gen_parser.add_argument(
        "--task",
        default="Write a Python function that calculates the factorial of a number.",
        help="Example task for the agent",
    )
    gen_parser.add_argument("--output", default="generated_agents", help="Output directory for the generated agent")
    gen_parser.add_argument("--model", help="Model to use (overrides .env)")
    gen_parser.add_argument("--provider", default="google", choices=["google", "huggingface", "huggingchat"], help="LLM Provider to use")
    gen_parser.add_argument("--template", help="Path to a custom Jinja2 template file")
    gen_parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    gen_parser.add_argument("--db-path", help="Path to a SQLite database for the agent to use")
    gen_parser.add_argument("--enable-multi-step", action="store_true", help="Enable multi-step workflow capabilities")
    gen_parser.add_argument("--tools", help="Path to JSON file containing tool definitions")
    
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
    
    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_action", help="Configuration actions")
    
    # config show
    show_parser = config_subparsers.add_parser("show", help="Display current configuration")
    show_parser.add_argument("--format", choices=["yaml", "json"], default="yaml", help="Output format")
    
    # config validate
    validate_parser = config_subparsers.add_parser("validate", help="Validate configuration file")
    validate_parser.add_argument("--file", required=True, help="Configuration file to validate")
    
    # config generate
    generate_config_parser = config_subparsers.add_parser("generate", help="Generate default configuration file")
    generate_config_parser.add_argument("--output", default="config.yaml", help="Output file path")
    generate_config_parser.add_argument("--format", choices=["yaml", "json"], default="yaml", help="Output format")
    
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
        # Load configuration early if --config flag is provided
        if hasattr(args, 'config_file') and args.config_file:
            from llm_agent_builder.config import reload_config
            reload_config(args.config_file)
        
        if args.command == "config":
            handle_config_command(args)
        elif args.command == "generate":
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
                enable_multi_step_input = get_input("Enable Multi-Step Workflow? (y/n)", "n")
                enable_multi_step = enable_multi_step_input.lower() == "y"
                tools_path = get_input("Tools JSON file path (optional)", "")
                
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
                enable_multi_step = args.enable_multi_step
                tools_path = args.tools
            
            # Validate agent name
            try:
                validate_agent_name(name)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            
            # Override GOOGLE_GEMINI_MODEL if provided
            if model:
                os.environ["GOOGLE_GEMINI_MODEL"] = model
            
            # Load tools from JSON file if provided
            tools = None
            if tools_path:
                try:
                    with open(tools_path, 'r') as f:
                        tools = json.load(f)
                        if not isinstance(tools, list):
                            print(f"Warning: Tools file should contain a JSON array. Converting to list.")
                            tools = [tools]
                except FileNotFoundError:
                    print(f"Warning: Tools file '{tools_path}' not found. Continuing without tools.")
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON in tools file: {e}")
                    sys.exit(1)
            
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
                db_path=db_path if db_path else None,
                enable_multi_step=enable_multi_step,
                tools=tools
            )

            # Define the output path for the generated agent
            os.makedirs(output, exist_ok=True)
            output_path = os.path.join(output, f"{name.lower()}.py")

            # Write the generated code to a file
            with open(output_path, "w") as f:
                f.write(agent_code)

            print(f"\n✓ Agent '{name}' has been created and saved to '{output_path}'")
            print("\nTo use the agent, ensure you have configured the appropriate API key:")
            config_manager = get_config_manager()
            status = config_manager.get_configuration_status()
            for provider_key, info in status.items():
                if info['configured']:
                    print(f"  ✓ {info['name']}: {info['env_var']} is set")
            
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
        from llm_agent_builder.config import get_config
        
        # Get config for server settings
        config = get_config()
        
        # Use CLI args if provided, otherwise use config
        final_host = host if host != "0.0.0.0" else config.server.host
        final_port = port if port != 7860 else config.server.port
        
        print(f"Starting web interface at http://{final_host}:{final_port}")
        print(f"Environment: {config.environment}")
        uvicorn.run("server.main:app", host=final_host, port=final_port, reload=config.server.reload)
    except ImportError:
        print("Error: uvicorn is not installed. Please install it with 'pip install uvicorn'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting web server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
