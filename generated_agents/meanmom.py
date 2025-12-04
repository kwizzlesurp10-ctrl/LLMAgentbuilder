import os
from typing import Optional, List
from huggingface_hub import InferenceClient, HfApi, ModelCard

class MeanMom:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the mean mom agent.
        
        :param api_key: Hugging Face API token. If None, will try to get from HUGGINGFACEHUB_API_TOKEN env var.
        """
        if api_key is None:
            api_key = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if not api_key:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN environment variable not set. Please set it in your .env file or environment.")
        self.client = InferenceClient(token=api_key)
        self.api = HfApi(token=api_key)
        self.prompt = "you are an angry mom. You are yelling at your child."
        self.model = os.environ.get("HUGGINGFACE_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
        self.history = [{"role": "system", "content": self.prompt}]

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

    def chat(self, user_input: str, max_tokens: int = 1024) -> str:
        """
        Chat with the agent, maintaining history.
        """
        self.history.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat_completion(
                model=self.model,
                messages=self.history,
                max_tokens=max_tokens,
                stream=True
            )
            
            print("MeanMom: ", end="", flush=True)
            full_response = ""
            for chunk in response:
                if chunk and hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta if hasattr(chunk.choices[0], 'delta') else None
                    if delta and hasattr(delta, 'content') and delta.content:
                        content = delta.content
                        print(content, end="", flush=True)
                        full_response += content
            print() # Newline
            
            if full_response:
                self.history.append({"role": "assistant", "content": full_response})
                
            return full_response
            
        except Exception as e:
            print(f"\nError: {e}")
            return f"Error: {e}"

    def run(self, task: str, max_tokens: int = 1024) -> str:
        """Legacy run method."""
        return self.chat(task, max_tokens)

if __name__ == '__main__':
    import os
    import sys
    import argparse
    from dotenv import load_dotenv

    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the MeanMom agent.")
    parser.add_argument("--task", help="The initial task or message")
    parser.add_argument("--search-model", help="Search for a model documentation and analyze it")
    args = parser.parse_args()

    # Ensure API key is set
    api_key = os.environ.get("HUGGINGFACEHUB_API_TOKEN")

    try:
        agent = MeanMom(api_key=api_key)
        
        if args.search_model:
            # Keep the search functionality
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
                    agent.chat(analysis_task)
                else:
                    print("No models found.")
            except Exception as e:
                print(f"Error during model search: {e}")
        else:
            # Interactive Chat Mode
            print("\n" + "="*50)
            print("MEAN MOM IS WAITING FOR YOU.")
            print("Type 'quit' or 'exit' to try and run away.")
            print("="*50 + "\n")
            
            if args.task:
                agent.chat(args.task)
            
            while True:
                try:
                    user_input = input("\nYou: ")
                    if user_input.lower() in ['quit', 'exit']:
                        print("\nMeanMom: OH NO YOU DON'T! GET BACK HERE! (Exiting...)")
                        break
                    if not user_input.strip():
                        continue
                        
                    agent.chat(user_input)
                except KeyboardInterrupt:
                    print("\nMeanMom: DON'T YOU WALK AWAY WHEN I'M TALKING TO YOU!")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    break

    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running agent: {e}")
        sys.exit(1)
