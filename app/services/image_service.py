# File: /app/services/image_service.py

import os
import openai
import requests
import logging
import base64
from app.schemas import SceneScript
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

RETRODIFFUSION_API_KEY = os.getenv("RETRODIFFUSION_API_KEY")
RETRODIFFUSION_URL = "https://api.retrodiffusion.ai/v1/inferences"

class ImageService:
    def __init__(self):
        if not RETRODIFFUSION_API_KEY:
            raise ValueError("RETRODIFFUSION_API_KEY is not set in .env")

    def generate_image_prompt(self, scene_script: SceneScript) -> str:
        """
        Uses OpenAI to generate a descriptive image prompt for Retro-Diffusion
        based on the scene script content.
        """
        # Combine all scene text lines into a descriptive passage
        scene_text = []
        for paragraph in scene_script.paragraphs:
            for line in paragraph.lines:
                # Include both dialogue and narrator text
                scene_text.append(f"{line.speaker}: {line.text}")
        combined_text = " ".join(scene_text)

        prompt = f"""
        You are an AI assistant that creates image prompts for a text-to-image model.
        Given the following scene description from a story, generate a single, concise, vivid, 
        and visually descriptive prompt suitable for a 256x256 illustration. 
        The prompt should focus on the visual depction of the elements of the scene. Don't waste words on describing the story, just a visceral description of what you want the user to see.

        Scene:
        {combined_text}

        Return only the prompt text, nothing else.
        """

        completion = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content.strip()

    def create_image(self, image_prompt: str) -> str:
        """
        Create an image using Retro-Diffusion API.
        Returns the path to the saved image file or empty string on error.
        Retries up to 5 times if the API call fails or returns no images.
        """
        max_retries = 5
        attempt = 0

        while attempt < max_retries:
            try:
                headers = {
                    "X-RD-Token": RETRODIFFUSION_API_KEY,
                }

                payload = {
                    "model": "RD_FLUX",
                    "width": 256,
                    "height": 256,
                    "prompt": image_prompt,
                    "num_images": 1
                }

                response = requests.post(RETRODIFFUSION_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    base64_images = data.get("base64_images", [])
                    if base64_images:
                        # Success path - proceed with saving the image
                        os.makedirs("static/images", exist_ok=True)
                        import uuid
                        filename = f"static/images/generated_{uuid.uuid4()}.png"
                        image_data = base64.b64decode(base64_images[0])
                        with open(filename, "wb") as f:
                            f.write(image_data)
                        return f"/{filename}"

                # If we get here, either the status code wasn't 200 or no images were returned
                attempt += 1
                if attempt < max_retries:
                    logger.warning(f"Retro-Diffusion API attempt {attempt} failed, retrying...")
                    continue
                else:
                    logger.error(f"Retro-Diffusion API failed after {max_retries} attempts. Last response: {response.text}")
                    return ""

            except Exception as e:
                attempt += 1
                if attempt < max_retries:
                    logger.warning(f"Error on attempt {attempt}, retrying: {str(e)}")
                    continue
                else:
                    logger.error(f"Failed after {max_retries} attempts. Last error: {str(e)}")
                    return ""

        return ""

    def generate_scene_image(self, scene_script: SceneScript) -> str:
        """
        High-level function to get image prompt and create image for a given scene.
        Returns the image file path or empty string on error.
        """
        try:
            image_prompt = self.generate_image_prompt(scene_script)
            image_path = self.create_image(image_prompt)
            return image_path
        except Exception as e:
            logger.error(f"Error generating scene image: {str(e)}")
            return ""
