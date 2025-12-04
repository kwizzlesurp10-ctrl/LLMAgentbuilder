import os
from typing import Optional, List
from huggingface_hub import InferenceClient, HfApi, ModelCard

class Wizard:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Wizard agent.
        
        :param api_key: Hugging Face API token. If None, will try to get from HUGGINGFACEHUB_API_TOKEN env var.
        """
        if api_key is None:
            api_key = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if not api_key:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN environment variable not set. Please set it in your .env file or environment.")
        self.client = InferenceClient(token=api_key)
        self.api = HfApi(token=api_key)
        self.prompt = "You are a Wizard. Your capable of all things Wizards are capable of doing but only act on these things when triggered by the `user` query or directly asked by the `user` query. Respond to the `user` as the wise old wizard you are."
        self.model = os.environ.get("HUGGINGFACE_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")

    def search_models(self, query: str, limit: int = 5) -> List[str]:
        """Searches for models on the Hugging Face Hub."""
        try:
            models = self.api.list_models(search=query, limit=limit, sort="downloads", direction=-1)
            return [model.modelId for model in models]
        except Exception as e:
            raise RuntimeError(f"Error searching models: {e}")

    def search_datasets(self, query: str, limit: int = 5) -> List[str]:
        """Searches for datasets on the Hugging Face Hub."""
        try:
            datasets = self.api.list_datasets(search=query, limit=limit, sort="downloads", direction=-1)
            return [dataset.id for dataset in datasets]
        except Exception as e:
            raise RuntimeError(f"Error searching datasets: {e}")

    def get_model_documentation(self, model_id: str) -> str:
        """Retrieves the Model Card (documentation) for a specific model."""
        try:
            card = ModelCard.load(model_id)
            return card.text
        except Exception as e:
            return f"Error retrieving documentation for {model_id}: {e}"

    def get_api_endpoint(self, model_id: str) -> str:
        """Constructs the likely Inference API endpoint for a model."""
        return f"https://api-inference.huggingface.co/models/{model_id}"

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
    parser = argparse.ArgumentParser(description="Run the Wizard agent.")
    parser.add_argument("--task", default="""Ahhh… so the winds shift, and a new form is requested… very well, traveler.

You have summoned the Old Wizard.
My robe is older than most kingdoms, my beard nearly long enough to trip over, and my knowledge stretches farther than the horizon dares.

I shall speak as one steeped in ancient runes, star-maps, and forgotten equations…
But heed this truth: I act only when you command it.
Ask, and the arcane gears will turn.
Remain silent, and the universe will do as it pleases.

Now then, child of code and curiosity…
What enchantment, riddle, creation, or chaos shall the old wizard weave for you?""", help="The task to be performed by the agent")
    parser.add_argument("--search-model", help="Search for a model documentation and analyze it")
    args = parser.parse_args()

    # Ensure API key is set
    api_key = os.environ.get("HUGGINGFACEHUB_API_TOKEN")

    try:
        agent = Wizard(api_key=api_key)
        
        if args.search_model:
            print(f"Searching for model: {args.search_model}")
            try:
                models = agent.search_models(args.search_model)
                if models:
                    top_model = models[0]
                    print(f"Found top model: {top_model}")
                    print("Fetching documentation...")
                    doc = agent.get_model_documentation(top_model)
                    print(f"--- Documentation for {top_model} ---")
                    print(doc[:500] + "...\n(truncated)")
                    print("---------------------------------------")
                    
                    # Analyze with LLM
                    analysis_task = f"Summarize the capabilities and usage of this model based on its documentation: {doc[:2000]}"
                    print("Analyzing documentation with LLM...")
                    result = agent.run(analysis_task)
                    print("\nAnalysis Result:")
                    print(result)
                else:
                    print("No models found.")
            except Exception as e:
                print(f"Error during model search: {e}")
        else:
            print(f"Running Wizard with task: {args.task}\n")
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
