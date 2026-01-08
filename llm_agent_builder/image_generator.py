from gradio_client import Client
import shutil
import os
from typing import Optional, Tuple, Any

class ImageGenerator:
    def __init__(self, space_id: str = "OnyxMunk/Juggernaut-XL-Diffusion"):
        self.space_id = space_id
        self.client: Optional[Client] = None

    def connect(self) -> None:
        """Connects to the Hugging Face Space."""
        if not self.client:
            print(f"Connecting to image generation Space: {self.space_id}...")
            try:
                self.client = Client(self.space_id)
                print("✓ Connected to image generation Space.")
            except Exception as e:
                print(f"✗ Failed to connect to image generation Space: {e}")
                raise

    def generate_avatar(self, prompt: str, output_path: str) -> Optional[str]:
        """
        Generates an avatar image based on the prompt and saves it to output_path.
        Returns the path to the saved image if successful, None otherwise.
        """
        if not self.client:
            try:
                self.connect()
            except Exception:
                return None

        print(f"Generating avatar for prompt: '{prompt}'...")
        try:
            # Using the API signature discovered during verification
            result = self.client.predict(
                prompt=prompt,
                negative_prompt="low quality, blurry, bad anatomy, text, watermark",
                seed=0,
                randomize_seed=True,
                width=1024,
                height=1024,
                guidance_scale=7.5,
                num_inference_steps=30,
                api_name="/infer"
            )

            # result is expected to be (image_path, seed)
            if result and isinstance(result, tuple) and len(result) > 0:
                # The first element could be a dict or a string path
                image_data = result[0]
                source_path = None
                
                if isinstance(image_data, dict) and 'path' in image_data:
                    source_path = image_data['path']
                elif isinstance(image_data, str):
                    source_path = image_data
                
                if source_path and os.path.exists(source_path):
                    shutil.copy(source_path, output_path)
                    print(f"✓ Avatar saved to: {output_path}")
                    return output_path
            
            print("✗ Failed to retrieve image from Space response.")
            return None

        except Exception as e:
            print(f"✗ Error generating avatar: {e}")
            return None
