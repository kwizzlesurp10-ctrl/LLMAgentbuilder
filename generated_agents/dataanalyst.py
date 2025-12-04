import os
from typing import Optional
from huggingface_hub import InferenceClient


class DataAnalyst:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DataAnalyst agent.
        
        :param api_key: Hugging Face API token. If None, will try to get from HUGGINGFACEHUB_API_TOKEN env var.
        """
        if api_key is None:
            api_key = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if not api_key:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN environment variable not set. Please set it in your .env file or environment.")
        self.client = InferenceClient(token=api_key)
        self.prompt = "You are a data analyst."
        self.model = os.environ.get("HUGGINGFACE_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")

    def run(self, task: str, max_tokens: int = 1024) -> str:
        """
        Run the agent with a given task.
        
        :param task: The task or question for the agent
        :param max_tokens: Maximum tokens to generate (default: 1024)
        :return: The agent's response
        """
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": task}
        ]
        
        try:
            response = self.client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                stream=False
            )
            if response and hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                if message and hasattr(message, 'content'):
                    return message.content
            raise RuntimeError("Invalid response format from API")
            
        except Exception as e:
            raise RuntimeError(f"Error calling Hugging Face API: {e}")

if __name__ == '__main__':
    import os
    import sys
    import argparse
    from dotenv import load_dotenv

    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the DataAnalyst agent.")
    parser.add_argument("--task", default="Analyze data.", help="The task to be performed by the agent")
    args = parser.parse_args()

    # Ensure API key is set
    api_key = os.environ.get("HUGGINGFACEHUB_API_TOKEN")

    try:
        agent = DataAnalyst(api_key=api_key)
        print(f"Running DataAnalyst with task: {args.task}\n")
        result = agent.run(args.task)
        print("Response:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running agent: {e}")
        sys.exit(1)