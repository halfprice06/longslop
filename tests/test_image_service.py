import os
from dotenv import load_dotenv
from app.schemas import SceneScript, Paragraph, SceneLine
from app.services.image_service import ImageService
import requests
import json

def create_sample_scene_script():
    return SceneScript(
        scene_title="A Romantic Evening",
        paragraphs=[
            Paragraph(
                lines=[
                    SceneLine(speaker="John", text="Hello, how are you?"),
                    SceneLine(speaker="Narrator", text="said John, smiling warmly."),
                    SceneLine(speaker="Jane", text="I'm fine, thank you."),
                    SceneLine(speaker="Narrator", text="Jane blushed slightly as she responded."),
                ]
            )
        ]
    )

def test_direct_api_call(prompt: str):
    """Make a direct API call to Retrodiffusion and print full response"""
    api_key = os.getenv("RETRODIFFUSION_API_KEY")
    headers = {
        "X-RD-Token": api_key,
    }
    
    payload = {
        "model": "RD_FLUX",
        "width": 256,
        "height": 256,
        "prompt": prompt,
        "num_images": 1
    }
    
    print("\nMaking direct API call to Retrodiffusion...")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post("https://api.retrodiffusion.ai/v1/inferences", headers=headers, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    try:
        data = response.json()
        # Create a copy of the response data with truncated base64 strings
        display_data = data.copy()
        if "base64_images" in display_data:
            display_data["base64_images"] = [
                f"{img[:50]}... (truncated)" for img in display_data["base64_images"]
            ]
        print("Response (base64 data truncated):")
        print(json.dumps(display_data, indent=2))
    except:
        print("Failed to parse response as JSON:")
        print(response.text[:200] + "... (truncated)")

def test_service_style_api_call():
    """Test API call with exact same parameters as the service"""
    api_key = os.getenv("RETRODIFFUSION_API_KEY")
    headers = {
        "X-RD-Token": api_key,
    }
    
    # Using same parameters as the service
    payload = {
        "model": "RD_FLUX",
        "width": 256,
        "height": 256,
        "prompt": "A test prompt that matches service style",
        "num_images": 1
    }
    
    print("\nTesting with service-style parameters...")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post("https://api.retrodiffusion.ai/v1/inferences", headers=headers, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        data = response.json()
        # Create a copy of the response data with truncated base64 strings
        display_data = data.copy()
        if "base64_images" in display_data:
            display_data["base64_images"] = [
                f"{img[:50]}... (truncated)" for img in display_data["base64_images"]
            ]
        print("Response (base64 data truncated):")
        print(json.dumps(display_data, indent=2))
    except:
        print("Failed to parse response as JSON:")
        print(response.text[:200] + "... (truncated)")

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    if not os.getenv("RETRODIFFUSION_API_KEY"):
        print("Please set RETRODIFFUSION_API_KEY in your .env file")
        return
    
    # Initialize the service
    try:
        image_service = ImageService()
    except ValueError as e:
        print(f"Error initializing ImageService: {e}")
        return
    
    # Create a sample scene script
    scene_script = create_sample_scene_script()
    
    # Test generate_image_prompt
    print("\nTesting image prompt generation...")
    try:
        image_prompt = image_service.generate_image_prompt(scene_script)
        print(f"Generated prompt: {image_prompt}")
        
        # Make direct API call with the generated prompt
        test_direct_api_call(image_prompt)
        
    except Exception as e:
        print(f"Error generating image prompt: {e}")
    
    # Test create_image
    print("\nTesting image creation through ImageService...")
    try:
        image_path = image_service.create_image(image_prompt)
        print(f"Generated image saved to: {image_path}")
    except Exception as e:
        print(f"Error creating image: {e}")
    
    # Test the high-level function
    print("\nTesting complete scene image generation...")
    try:
        final_path = image_service.generate_scene_image(scene_script)
        print(f"Final image saved to: {final_path}")
    except Exception as e:
        print(f"Error in complete scene generation: {e}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the new test
    test_service_style_api_call()
    
    # Run original main() if needed
    # main() 