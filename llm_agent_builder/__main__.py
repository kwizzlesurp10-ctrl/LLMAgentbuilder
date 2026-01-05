"""
Unified entry point for LLM Agent Builder.

This module provides intelligent mode detection to route between:
- Web interface (default when no arguments provided)
- CLI commands (when CLI subcommands are used)
"""
import sys
import argparse


def main() -> None:
    """
    Main entry point with intelligent mode detection.
    
    Modes:
    - Web Mode: Launched when no args provided or --serve flag used
    - CLI Mode: Launched when CLI commands (generate, list, test, batch) provided
    - Help Mode: Show usage when --help provided
    """
    # Quick check: if a CLI command is detected, route directly to CLI
    if len(sys.argv) > 1:
        # Check for CLI commands - route directly to CLI if found
        cli_commands = {"generate", "list", "test", "batch"}
        if sys.argv[1] in cli_commands:
            run_cli()
            return
        # Check for --cli flag - route to CLI with flag removed
        if "--cli" in sys.argv:
            # Create a copy of sys.argv without the --cli flag
            import copy
            original_argv = sys.argv
            sys.argv = [arg for arg in sys.argv if arg != "--cli"]
            try:
                run_cli()
            finally:
                # Restore original argv
                sys.argv = original_argv
            return
    
    # Parse arguments to determine mode
    parser = argparse.ArgumentParser(
        prog="llm-agent-builder",
        description="LLM Agent Builder - Generate AI agents via CLI or web interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True
    )
    
    # Mode flags
    parser.add_argument("--serve", action="store_true", help="Launch web interface (default)")
    parser.add_argument("--host", default="0.0.0.0", help="Web server host (web mode only)")
    parser.add_argument("--port", type=int, default=7860, help="Web server port (web mode only)")
    
    # Only parse if we have args, otherwise default to web mode
    if len(sys.argv) == 1:
        # No arguments provided - default to web mode
        launch_web_server("0.0.0.0", 7860)
        return
    
    args = parser.parse_args()
    
    # If we get here with --serve, launch web
    if args.serve:
        launch_web_server(args.host, args.port)
    else:
        # This should not be reached in normal operation
        # If it is, it means an unexpected argument combination was provided
        import logging
        logging.warning("Unexpected code path reached in main(). Showing help.")
        show_help()
        sys.exit(0)


def show_help() -> None:
    """Display help message for unified entry point."""
    help_text = """
LLM Agent Builder - Generate AI agents via CLI or web interface

USAGE:
    llm-agent-builder [MODE] [OPTIONS]

MODES:
    (default)              Launch web interface (no arguments needed)
    --serve                Explicitly launch web interface
    --cli                  Force CLI mode
    generate               Generate a new agent (CLI)
    list                   List all generated agents (CLI)
    test                   Test a generated agent (CLI)
    batch                  Batch generate agents from JSON (CLI)

WEB MODE OPTIONS:
    --host HOST            Host to bind web server to (default: 0.0.0.0)
    --port PORT            Port to bind web server to (default: 7860)

EXAMPLES:
    # Launch web interface (default)
    llm-agent-builder
    llm-agent-builder --serve
    llm-agent-builder --serve --host 127.0.0.1 --port 8080
    
    # Use CLI commands
    llm-agent-builder generate --name MyAgent --prompt "..." --task "..."
    llm-agent-builder list
    llm-agent-builder test generated_agents/myagent.py --task "Test this"
    llm-agent-builder batch agents.json
    
    # Force CLI mode (for interactive agent generation)
    llm-agent-builder --cli generate

For detailed CLI command help:
    llm-agent-builder generate --help
    llm-agent-builder list --help
    llm-agent-builder test --help
    llm-agent-builder batch --help

For more information, visit:
    https://github.com/kwizzlesurp10-ctrl/LLMAgentbuilder
"""
    print(help_text)


def launch_web_server(host: str, port: int) -> None:
    """Launch the web interface."""
    from .server_runner import run_web_server
    print("Launching web interface...")
    run_web_server(host=host, port=port)


def run_cli() -> None:
    """Run CLI mode by delegating to the CLI module."""
    # Import and run the CLI
    from .cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
