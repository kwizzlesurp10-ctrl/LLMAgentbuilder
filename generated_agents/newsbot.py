import anthropic
import os
from typing import Optional, List, Dict, Any

import sqlite3



class NewsBot:
    def __init__(self, api_key):
        
        from huggingface_hub import InferenceClient
        self.client = InferenceClient(token=api_key)
        self.model = "meta-llama/Meta-Llama-3-8B-Instruct"
        
        self.prompt = "You are a helpful assistant that specializes in writing Python code."
        
        
        self.db_path = "workflow.db"
        self.prompt += "\n\nYou have access to a SQLite database. You can query it using the 'query_database' tool."
        # Add database tool definition
        db_tool = {
            "name": "query_database",
            "description": "Execute a SQL query against the SQLite database. Use this to retrieve information.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        }
        if not hasattr(self, 'tools'):
            self.tools = []
        self.tools.append(db_tool)
        

    

    
    def query_database(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query against the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return {"status": "success", "results": results}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    

    

    def run(self, task: str):
        
        
        
        messages = [{"role": "system", "content": self.prompt}, {"role": "user", "content": task}]
        response = self.client.chat_completion(
            model=self.model,
            messages=messages,
            max_tokens=2048,
            stream=False
        )
        # Note: Tool calling with HF InferenceClient is model-dependent and may require different handling.
        # For this implementation, we'll focus on text generation.
        return response.choices[0].message.content
        

if __name__ == '__main__':
    import os
    import argparse
    from dotenv import load_dotenv

    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the NewsBot agent.")
    parser.add_argument("--task", default="List the latest alerts from the database", help="The task to be performed by the agent")
    args = parser.parse_args()

    # Ensure API key is set
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not api_key:
        raise ValueError("API key not found. Please set ANTHROPIC_API_KEY or HUGGINGFACEHUB_API_TOKEN.")

    try:
        agent = NewsBot(api_key=api_key)
        print(f"Running NewsBot with task: {args.task}\n")
        result = agent.run(args.task)
        print("Response:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    except Exception as e:
        print(f"Error running agent: {e}")