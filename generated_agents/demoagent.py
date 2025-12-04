import anthropic
import os
from typing import Optional, List, Dict, Any



class DemoAgent:
    def __init__(self, api_key):
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
        self.prompt = "You are a helpful coding assistant"
        
        

    

    

    

    def run(self, task: str):
        
        
        
        response = self.client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=2048,
            system=self.prompt,
            messages=[
                {"role": "user", "content": task}
            ]
        )
        
        
        
        return response.content[0].text
        

if __name__ == '__main__':
    import os
    import argparse
    from dotenv import load_dotenv

    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the DemoAgent agent.")
    parser.add_argument("--task", default="Write a Python function to calculate fibonacci numbers", help="The task to be performed by the agent")
    args = parser.parse_args()

    # Ensure API key is set
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not api_key:
        raise ValueError("API key not found. Please set ANTHROPIC_API_KEY or HUGGINGFACEHUB_API_TOKEN.")

    try:
        agent = DemoAgent(api_key=api_key)
        print(f"Running DemoAgent with task: {args.task}\n")
        result = agent.run(args.task)
        print("Response:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    except Exception as e:
        print(f"Error running agent: {e}")