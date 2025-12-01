import os
import argparse
import sys
from typing import Optional
from llm_agent_builder.agent_builder import AgentBuilder
from dotenv import load_dotenv

def get_input(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value if value else default

def main() -> None:
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate an LLM agent using Anthropic API.")
    parser.add_argument("--name", default="MyAwesomeAgent", help="Name of the agent to be built")
    parser.add_argument("--prompt", default="You are a helpful assistant that specializes in writing Python code.", help="System prompt for the agent")
    parser.add_argument("--task", default="Write a Python function that calculates the factorial of a number.", help="Example task for the agent")
    parser.add_argument("--output", default="generated_agents", help="Output directory for the generated agent")
    parser.add_argument("--model", help="Anthropic model to use (overrides .env)")
    parser.add_argument("--provider", default="anthropic", choices=["anthropic", "huggingface"], help="LLM Provider to use (anthropic or huggingface)")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")

    # Check if we should run in interactive mode (explicit flag or no args)
    # Note: We want to preserve the ability to run with defaults using a flag if needed, 
    # but for now let's say if NO args are passed, we default to interactive? 
    # Or maybe just add an --interactive flag. 
    # The plan said "If no arguments are provided, use input()".
    # But argparse sets defaults. 
    # Let's stick to the plan: if len(sys.argv) == 1, go interactive.
    
    if len(sys.argv) == 1:
        print("No arguments provided. Starting interactive mode...")
        name = get_input("Agent Name", "MyAwesomeAgent")
        prompt = get_input("System Prompt", "You are a helpful assistant that specializes in writing Python code.")
        task = get_input("Example Task", "Write a Python function that calculates the factorial of a number.")
        output = get_input("Output Directory", "generated_agents")
        default_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        model = get_input("Anthropic Model", default_model)
        provider = get_input("Provider (anthropic/huggingface)", "anthropic")
        
        args = argparse.Namespace(
            name=name,
            prompt=prompt,
            task=task,
            output=output,
            model=model,
            provider=provider
        )
    else:
        args = parser.parse_args()

    # Override ANTHROPIC_MODEL if provided via CLI or Interactive
    if args.model:
        os.environ["ANTHROPIC_MODEL"] = args.model

    # Create an instance of the AgentBuilder
    builder = AgentBuilder()

    # Generate the agent code
    # We need to handle the model argument being passed only if it exists, but build_agent has a default.
    # However, we now have a provider argument too.
    agent_code = builder.build_agent(
        agent_name=args.name, 
        prompt=args.prompt, 
        example_task=args.task, 
        model=args.model if args.model else ("claude-3-5-sonnet-20241022" if args.provider == "anthropic" else "HuggingFaceH4/zephyr-7b-beta"),
        provider=args.provider
    )

    # Define the output path for the generated agent
    os.makedirs(args.output, exist_ok=True)
    output_path = os.path.join(args.output, f"{args.name.lower()}.py")

    # Write the generated code to a file
    with open(output_path, "w") as f:
        f.write(agent_code)

    print(f"Agent '{args.name}' has been created and saved to '{output_path}'")
    print("To use the agent, you need to set the ANTHROPIC_API_KEY environment variable.")

if __name__ == "__main__":
    main()
