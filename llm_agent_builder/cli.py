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
from llm_agent_builder.image_generator import ImageGenerator
from llm_agent_builder.huggingface_utils import deploy_to_hf
from llm_agent_builder.presets import PresetManager
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
    
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not api_key:
        print("Error: API key not found. Please set ANTHROPIC_API_KEY or HUGGINGFACEHUB_API_TOKEN.")
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
                model = config.get("model", "claude-3-5-sonnet-20241022")
                provider = config.get("provider", "anthropic")
                
                docs_path = config.get("docs_path")
                swarm_config = config.get("swarm_config")
                agents = config.get("agents")
                
                if not prompt or not task:
                    # Swarms might not have a simple prompt/task in the top level config depending on structure, 
                    # but if it's a swarm, we might expect 'agents' list.
                    if not swarm_config and not agents:
                         print(f"  [{i}] Skipping '{agent_name}': missing prompt or task")
                         continue
                
                agent_code = builder.build_agent(
                    agent_name=agent_name,
                    prompt=prompt,
                    example_task=task,
                    model=model,
                    provider=provider,
                    docs_path=docs_path,
                    swarm_config=swarm_config,
                    agents=agents
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
    gen_parser.add_argument("--provider", default="anthropic", choices=["anthropic", "huggingface", "anytool"], help="LLM Provider to use")
    gen_parser.add_argument("--template", help="Path to a custom Jinja2 template file")
    gen_parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    gen_parser.add_argument("--db-path", help="Path to a SQLite database for the agent to use")
    gen_parser.add_argument("--docs-path", help="Path to a directory of documents for RAG (Knowledge Base)")
    gen_parser.add_argument("--preset", help="Name or ID of a preset to use as a template")
    
    # List subcommand
    list_parser = subparsers.add_parser("list", help="List all generated agents")
    list_parser.add_argument("--output", default="generated_agents", help="Output directory to search")
    
    # Presets subcommand
    presets_parser = subparsers.add_parser("presets", help="Manage agent presets")
    presets_subparsers = presets_parser.add_subparsers(dest="preset_command", help="Preset commands")
    
    presets_list_parser = presets_subparsers.add_parser("list", help="List available presets")
    
    presets_show_parser = presets_subparsers.add_parser("show", help="Show details of a preset")
    presets_show_parser.add_argument("name", help="Name or ID of the preset")
    
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
    
    # Deploy subcommand
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to Hugging Face Spaces")
    deploy_parser.add_argument("--repo", help="Target repository ID (e.g., 'username/repo-name')")
    deploy_parser.add_argument("--name", help="Name for the Space (used if --repo is not provided)")
    deploy_parser.add_argument("--sdk", default="docker", choices=["docker", "gradio", "streamlit", "static"], help="Space SDK type")
    deploy_parser.add_argument("--private", action="store_true", help="Make the Space private")
    deploy_parser.add_argument("--public", type=str, default="true", help="Set to 'false' for private")
    deploy_parser.add_argument("--type", help="Legacy flag for repo-type or SDK type")
    
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
        if args.command == "presets":
            manager = PresetManager()
            if args.preset_command == "list":
                presets = manager.list_presets()
                if not presets:
                    print("No presets found.")
                else:
                    print(f"\nFound {len(presets)} preset(s):")
                    print("-" * 60)
                    for preset in presets:
                        print(f"  • {preset.name} (ID: {preset.id}) - {preset.description}")
                    print("-" * 60)
            elif args.preset_command == "show":
                preset = manager.get_preset(args.name)
                if not preset:
                    print(f"Error: Preset '{args.name}' not found.")
                    sys.exit(1)
                print(f"\nPreset: {preset.name}")
                print(f"ID: {preset.id}")
                print(f"Version: {preset.version}")
                print(f"Description: {preset.description}")
                print(f"Provider: {preset.config.provider}")
                print(f"Model: {preset.config.model}")
                print("-" * 60)
                print("System Prompt:")
                print(preset.config.system_prompt)
                print("-" * 60)
                print("Example Task:")
                print(preset.config.example_task)
                if preset.config.tools:
                    print("-" * 60)
                    print(f"Tools ({len(preset.config.tools)}):")
                    for tool in preset.config.tools:
                        print(f"  - {tool.get('name')}: {tool.get('description')}")
                print("-" * 60)
            else:
                presets_parser.print_help()

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
                # Offer presets in interactive mode
                use_preset = get_input("Use a preset template? (Y/n)", "n")
                if use_preset.lower() == 'y':
                    manager = PresetManager()
                    presets = manager.list_presets()
                    if not presets:
                        print("No presets available.")
                        preset_name = None
                    else:
                        print("\nAvailable Presets:")
                        for i, p in enumerate(presets, 1):
                            print(f"{i}. {p.name} - {p.description}")
                        
                        choice = get_input("Select preset number", "1")
                        try:
                            preset = presets[int(choice)-1]
                            preset_name = preset.id
                        except (ValueError, IndexError):
                            print("Invalid selection.")
                            preset_name = None
                else:
                    preset_name = None

                if preset_name:
                    manager = PresetManager()
                    preset = manager.get_preset(preset_name)
                    if not preset:
                        print(f"Error: Preset '{preset_name}' not found.")
                        sys.exit(1)
                    
                    print(f"Loaded preset: {preset.name}")
                    name = get_input("Agent Name", preset.name, validator=validate_agent_name)
                    prompt = get_input("System Prompt", preset.config.system_prompt)
                    task = get_input("Example Task", preset.config.example_task)
                    output = get_input("Output Directory", args.output)
                    model = get_input("Model", preset.config.model)
                    provider = get_input("Provider (anthropic/huggingface/anytool)", preset.config.provider)
                    template = get_input("Custom Template Path (optional)", "")
                    db_path = get_input("SQLite Database Path (optional)", "")
                    docs_path = get_input("Knowledge Base Path (optional)", "")
                    tools = preset.config.tools
                else:
                    name = get_input("Agent Name", args.name, validator=validate_agent_name)
                    prompt = get_input("System Prompt", args.prompt)
                    task = get_input("Example Task", args.task)
                    output = get_input("Output Directory", args.output)
                    default_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
                    model = get_input("Model", default_model)
                    provider = get_input("Provider (anthropic/huggingface/anytool)", args.provider)
                    template = get_input("Custom Template Path (optional)", "")
                    db_path = get_input("SQLite Database Path (optional)", "")
                    docs_path = get_input("Knowledge Base Path (optional)", "")
                    tools = None
                
                # Validate provider
                if provider not in ["anthropic", "huggingface", "anytool"]:
                    print(f"Error: Invalid provider '{provider}'. Must be 'anthropic', 'huggingface', or 'anytool'.")
                    sys.exit(1)
            else:
                tools = None
                if args.preset:
                    manager = PresetManager()
                    preset = manager.get_preset(args.preset)
                    if not preset:
                        print(f"Error: Preset '{args.preset}' not found.")
                        sys.exit(1)
                    print(f"Using preset: {preset.name}")
                    # Use preset values if args are default or empty, otherwise override
                    name = args.name if args.name != "MyAwesomeAgent" else preset.name
                    prompt = args.prompt if args.prompt != "You are a helpful assistant that specializes in writing Python code." else preset.config.system_prompt
                    task = args.task if args.task != "Write a Python function that calculates the factorial of a number." else preset.config.example_task
                    model = args.model if args.model else preset.config.model
                    provider = args.provider if args.provider != "anthropic" else preset.config.provider
                    tools = preset.config.tools
                else:
                    name = args.name
                    prompt = args.prompt
                    task = args.task
                    model = args.model
                    provider = args.provider
                
                output = args.output
                template = args.template
                db_path = args.db_path
                docs_path = args.docs_path
            
            # Validate agent name
            try:
                validate_agent_name(name)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            
            # Override ANTHROPIC_MODEL if provided
            if model:
                os.environ["ANTHROPIC_MODEL"] = model
            
            # Create an instance of the AgentBuilder
            builder = AgentBuilder(template_path=template if template else None)
            
            # Generate the agent code
            if not model:
                if provider == "anthropic":
                    default_model = "claude-3-5-sonnet-20241022"
                elif provider == "huggingface":
                    default_model = "meta-llama/Meta-Llama-3-8B-Instruct"
                elif provider == "anytool":
                    default_model = "openrouter/anthropic/claude-sonnet-4.5"
                else:
                    default_model = "claude-3-5-sonnet-20241022"
            else:
                default_model = model

            agent_code = builder.build_agent(
                agent_name=name, 
                prompt=prompt, 
                example_task=task, 
                model=default_model,
                provider=provider,
                db_path=db_path if db_path else None,
                docs_path=docs_path if docs_path else None,
                tools=tools
            )
            
            # Define the output path for the generated agent
            os.makedirs(output, exist_ok=True)
            output_path = os.path.join(output, f"{name.lower()}.py")
            
            # Write the generated code to a file
            with open(output_path, "w") as f:
                f.write(agent_code)
            
            print(f"\n✓ Agent '{name}' has been created and saved to '{output_path}'")
            print("To use the agent, you need to set the ANTHROPIC_API_KEY environment variable.")
            
            # Offer to generate avatar
            if args.interactive or no_args_provided:
                generate_avatar = get_input("Generate avatar for this agent? (Y/n)", "Y")
                if generate_avatar.lower() == "y":
                    avatar_prompt = f"A portrait of {name}, {prompt}"
                    # Truncate prompt if too long to avoid issues
                    if len(avatar_prompt) > 500:
                        avatar_prompt = avatar_prompt[:497] + "..."
                    
                    avatar_path = os.path.join(output, f"{name.lower()}_avatar.webp")
                    generator = ImageGenerator()
                    generator.generate_avatar(avatar_prompt, avatar_path)
            
        elif args.command == "list":
            list_agents(args.output)
            
        elif args.command == "test":
            test_agent(args.agent_path, args.task)
            
        elif args.command == "batch":
            batch_generate(args.config_file, args.output, args.template)
            
        elif args.command == "web":
            run_web_server(args.host, args.port)
            
        elif args.command == "deploy":
            repo_id = args.repo or args.name or "LLMAgentBuilder"
            sdk = args.sdk
            
            # Handle legacy/redundant flags from user request
            if args.type == "docker":
                sdk = "docker"
            
            is_private = args.private or (args.public.lower() == "false")
            
            print(f"Starting deployment of '{repo_id}' to Hugging Face Spaces...")
            try:
                url = deploy_to_hf(
                    repo_id=repo_id,
                    private=is_private,
                    space_sdk=sdk
                )
                print(f"\n✓ Deployment successful!")
                print(f"Your Space is available at: {url}")
            except Exception as e:
                print(f"Error during deployment: {e}")
                sys.exit(1)
            
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
