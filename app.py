import gradio as gr
import os
import sys
import importlib.util
import inspect
from dotenv import load_dotenv
from llm_agent_builder.agent_builder import AgentBuilder

# Load environment variables
load_dotenv()

# Initialize Builder
builder = AgentBuilder()

# Ensure generated_agents directory exists
os.makedirs("generated_agents", exist_ok=True)

def get_available_agents():
    """List all generated agent files."""
    if not os.path.exists("generated_agents"):
        return []
    files = [f for f in os.listdir("generated_agents") if f.endswith(".py") and f != "__init__.py"]
    return sorted(files)

def generate(name, prompt, example_task, model, provider, enable_multi_step):
    try:
        # Normalize provider
        provider = provider.lower()
        
        # Generate code
        code = builder.build_agent(
            agent_name=name,
            prompt=prompt,
            example_task=example_task,
            model=model,
            provider=provider,
            enable_multi_step=enable_multi_step
        )
        
        # Save to file for download
        os.makedirs("generated_agents", exist_ok=True)
        filename = f"generated_agents/{name.lower().replace(' ', '_')}.py"
        with open(filename, "w") as f:
            f.write(code)
            
        return code, filename, f"✅ Successfully generated {name}!", gr.update(choices=get_available_agents())
    except Exception as e:
        return f"# Error generating code\n{str(e)}", None, f"❌ Error: {str(e)}", gr.update()

def update_model_placeholder(provider):
    if provider == "google":
        return gr.update(value="gemini-1.5-pro")
    elif provider == "openai":
        return gr.update(value="gpt-4o")
    elif provider == "huggingface":
        return gr.update(value="meta-llama/Meta-Llama-3-8B-Instruct")
    elif provider == "huggingchat":
        return gr.update(value="meta-llama/Meta-Llama-3-70B-Instruct")
    return gr.update()

def run_agent_test(agent_file, task_input):
    if not agent_file:
        return "Please select an agent first."
    if not task_input:
        return "Please enter a task."
        
    try:
        # Construct path
        file_path = os.path.join("generated_agents", agent_file)
        
        # Dynamic import
        spec = importlib.util.spec_from_file_location("agent_module", file_path)
        if spec is None or spec.loader is None:
            return f"Could not load agent from {file_path}"
            
        module = importlib.util.module_from_spec(spec)
        sys.modules["agent_module"] = module
        spec.loader.exec_module(module)
        
        # Find the agent class (heuristic: class name matches file name or is the only custom class)
        # We'll look for a class that has a 'run' method
        agent_class = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == "agent_module":
                if hasattr(obj, 'run'):
                    agent_class = obj
                    break
        
        if not agent_class:
            return "Could not find a valid Agent class (must have a 'run' method) in the file."

        # specific key loading logic based on what usually exists
        # The templates look for specific env vars passed to __init__
        # We try to grab the right one based on common patterns or just pass what we have
        
        # Note: The templates expect 'api_key' in __init__.
        # We can try to infer which key to use or pass None (if the agent handles env vars internally)
        # Looking at templates:
        # - Google: uses api_key arg -> os.environ.get("GOOGLE_GEMINI_KEY")
        # - HF: uses api_key arg -> os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        # - OpenAI: uses api_key arg -> os.environ.get("OPENAI_API_KEY")
        
        # Let's try to pass the most likely key if available, otherwise rely on the agent's internal fallback
        api_key = None
        if "GOOGLE_GEMINI_KEY" in os.environ:
             api_key = os.environ["GOOGLE_GEMINI_KEY"]
        elif "HUGGINGFACEHUB_API_TOKEN" in os.environ:
             api_key = os.environ["HUGGINGFACEHUB_API_TOKEN"]
        elif "OPENAI_API_KEY" in os.environ:
             api_key = os.environ["OPENAI_API_KEY"]
             
        # Instantiate
        try:
            # Some templates might default to env var if None is passed, some might fail.
            # Best bet is to try to instantiate with what we found, or let it fail and catch.
            # Looking at template logic: `if api_key is None: api_key = os.environ.get(...)`
            # So passing None is safe if Env is set.
            agent_instance = agent_class(api_key=api_key) 
        except Exception as init_err:
            return f"Error initializing agent: {str(init_err)}\n(Check if your API keys are set in .env)"

        # Run
        result = agent_instance.run(task_input)
        return result

    except Exception as e:
        import traceback
        return f"Error during execution:\n{traceback.format_exc()}"

# UI Layout
with gr.Blocks(title="LLM Agent Builder") as demo:
    gr.Markdown(
        """
        # 🤖 LLM Agent Builder
        Scaffold, generate, and **test** AI agents using various providers (Google, Hugging Face, OpenAI).
        """
    )
    
    with gr.Tabs():
        with gr.Tab("🛠️ Build Agent"):
            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Group():
                        gr.Markdown("### 1. Configuration")
                        name_input = gr.Textbox(label="Agent Name", placeholder="e.g. CodeReviewer", value="MyAgent")
                        provider_input = gr.Dropdown(
                            choices=["google", "huggingface", "huggingchat", "openai"], 
                            value="google", 
                            label="Provider",
                            info="Select the LLM provider you want to use."
                        )
                        model_input = gr.Textbox(
                            label="Model Name", 
                            value="gemini-1.5-pro", 
                            placeholder="e.g. gemini-1.5-pro",
                            info="Specific model ID to use."
                        )
                        multi_step_input = gr.Checkbox(
                            label="Enable Multi-Step Tools", 
                            value=False,
                            info="Allow the agent to perform multiple steps/tool calls."
                        )
                    
                with gr.Column(scale=1):
                    with gr.Group():
                        gr.Markdown("### 2. Instructions")
                        prompt_input = gr.Textbox(
                            label="System Prompt", 
                            lines=6, 
                            placeholder="You are a helpful assistant...", 
                            value="You are a helpful AI assistant specialized in Python development."
                        )
                        task_input = gr.Textbox(
                            label="Example Task (for testing)", 
                            lines=3, 
                            placeholder="Summarize this text...", 
                            value="Write a 'Hello World' function in Python."
                        )

            generate_btn = gr.Button("🚀 Generate Agent Code", variant="primary", size="lg")
            
            gr.Markdown("### 3. Output")
            status_output = gr.Markdown("")
            
            with gr.Row():
                code_output = gr.Code(label="Generated Python Code", language="python", lines=20)
                file_output = gr.File(label="Download Agent File")

        with gr.Tab("🧪 Test Agent"):
            gr.Markdown("### Test your generated agents directly here.")
            with gr.Row():
                with gr.Column(scale=1):
                    agent_selector = gr.Dropdown(
                        label="Select Agent", 
                        choices=get_available_agents(),
                        interactive=True,
                        info="Select a generated agent file."
                    )
                    refresh_btn = gr.Button("🔄 Refresh List", size="sm")
                    
                    test_task_input = gr.Textbox(
                        label="Test Input", 
                        lines=4, 
                        placeholder="Enter a prompt for your agent...",
                        value="Who are you and what can you do?"
                    )
                    run_test_btn = gr.Button("▶️ Run Agent", variant="primary")
                
                with gr.Column(scale=1):
                    test_output = gr.Markdown(label="Agent Response")

    # Event Wiring
    provider_input.change(fn=update_model_placeholder, inputs=provider_input, outputs=model_input)
    
    # Generate updates the agent list too
    generate_btn.click(
        fn=generate,
        inputs=[name_input, prompt_input, task_input, model_input, provider_input, multi_step_input],
        outputs=[code_output, file_output, status_output, agent_selector]
    )
    
    # Test Tab
    refresh_btn.click(fn=lambda: gr.update(choices=get_available_agents()), outputs=agent_selector)
    run_test_btn.click(
        fn=run_agent_test,
        inputs=[agent_selector, test_task_input],
        outputs=[test_output]
    )
    
    with gr.Accordion("📝 Feedback", open=False):
        gr.Markdown("Help us improve the Agent Builder!")
        feedback_input = gr.Textbox(label="Your Feedback")
        feedback_btn = gr.Button("Submit Feedback")
        feedback_msg = gr.Markdown()
        
        def submit_feedback(text):
            if not text:
                return "Please enter some text."
            with open("feedback.log", "a") as f:
                f.write(f"{text}\n")
            return "✅ Thanks for your feedback!"
            
        feedback_btn.click(submit_feedback, inputs=[feedback_input], outputs=[feedback_msg])
        
    gr.Markdown("---\n*Run locally or deploy to Hugging Face Spaces.*")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())