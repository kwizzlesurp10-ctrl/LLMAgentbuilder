
import os
import sys
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_agent_builder.agent_builder import AgentBuilder
from llm_agent_builder.agent_engine import AgentEngine, ExecutionStatus

load_dotenv()

def generate_agent(name, prompt, task, model, provider):
    try:
        if not name or not prompt:
            return "Error: Name and Prompt are required."
            
        builder = AgentBuilder()
        code = builder.build_agent(
            agent_name=name,
            prompt=prompt,
            example_task=task,
            model=model,
            provider=provider
        )
        return code
    except Exception as e:
        return f"Error generating agent: {str(e)}"

def run_agent_test(agent_source, task):
    """
    Execute an agent with a given task.
    This function mimics the one causing the traceback but with robust error handling.
    """
    try:
        if not agent_source:
             return "Error: No agent source provided."

        # Initialize engine
        # In a real deployment, keys should be env vars
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if not api_key:
            return "Error: No API key found in environment variables."
            
        engine = AgentEngine(api_key=api_key)
        
        # Execute
        result = engine.execute_with_timeout(agent_source, task)
        
        if result.status == ExecutionStatus.SUCCESS:
            return result.output
        else:
            return f"Execution Failed ({result.status.value}):\n{result.error}\n\nOutput:\n{result.output}"
            
    except Exception as e:
        return f"System Error: {str(e)}"

# Gradio Interface
with gr.Blocks(title="LLM Agent Builder") as demo:
    gr.Markdown("# LLM Agent Builder & Runner")
    
    with gr.Tab("Generate Agent"):
        name_input = gr.Textbox(label="Agent Name", value="MyAgent")
        prompt_input = gr.Textbox(label="System Prompt", lines=5, value="You are a helpful assistant.")
        task_input = gr.Textbox(label="Example Task", lines=2, value="Say hello.")
        model_input = gr.Dropdown(choices=["claude-3-5-sonnet-20241022", "meta-llama/Meta-Llama-3-8B-Instruct", "openrouter/anthropic/claude-sonnet-4.5"], label="Model", value="claude-3-5-sonnet-20241022")
        provider_input = gr.Dropdown(choices=["anthropic", "huggingface", "anytool"], label="Provider", value="anthropic")
        
        generate_btn = gr.Button("Generate Agent Code")
        code_output = gr.Code(label="Generated Python Code", language="python")
        
        generate_btn.click(
            generate_agent,
            inputs=[name_input, prompt_input, task_input, model_input, provider_input],
            outputs=code_output
        )
    
    with gr.Tab("Run Agent"):
        gr.Markdown("Test your generated agent code directly.")
        agent_code_input = gr.Code(label="Agent Code", language="python")
        test_task_input = gr.Textbox(label="Task", placeholder="Enter a task for the agent...")
        run_btn = gr.Button("Execute Agent")
        execution_output = gr.Textbox(label="Execution Result", lines=10)
        
        run_btn.click(
            run_agent_test,
            inputs=[agent_code_input, test_task_input],
            outputs=execution_output
        )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
