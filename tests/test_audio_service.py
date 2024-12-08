import os
from dotenv import load_dotenv
from app.schemas import SceneScript, Paragraph, SceneLine
from app.services.audio_service import AudioService
import requests
import json

def create_sample_scene_script():
    return SceneScript(
        scene_title="A Quiet Conversation",
        paragraphs=[
            Paragraph(
                lines=[
                    SceneLine(speaker="John", text="Have you ever seen such a beautiful sunset?"),
                    SceneLine(speaker="Narrator", text="John gestured towards the horizon."),
                    SceneLine(speaker="Mary", text="It's absolutely breathtaking."),
                    SceneLine(speaker="Narrator", text="Mary's eyes sparkled as she gazed at the sky."),
                ]
            )
        ]
    )

def test_direct_elevenlabs_api_call(text: str, voice_id: str):
    """Make a direct API call to ElevenLabs and print full response"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    print("\nMaking direct API call to ElevenLabs...")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("Successfully received audio data")
        print(f"Audio size: {len(response.content)} bytes")
    else:
        print("Error Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text[:200] + "... (truncated)")

def test_voice_assignment():
    """Test the voice assignment functionality"""
    audio_service = AudioService()
    
    # Test with a set of speakers
    test_speakers = {"Narrator", "John", "Mary", "Sarah"}
    voice_mapping = audio_service.assign_voices_to_speakers(test_speakers)
    
    print("\nTesting voice assignment...")
    print(f"Input speakers: {test_speakers}")
    print(f"Voice mapping: {json.dumps(voice_mapping, indent=2)}")
    
    # Verify that each speaker has a unique voice
    assert len(voice_mapping) == len(test_speakers), "Not all speakers were assigned voices"
    assert "Narrator" in voice_mapping, "Narrator must be assigned a voice"

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("Please set ELEVENLABS_API_KEY in your .env file")
        return
    
    # Initialize the service
    try:
        audio_service = AudioService()
    except Exception as e:
        print(f"Error initializing AudioService: {e}")
        return
    
    # Create a sample scene script
    scene_script = create_sample_scene_script()
    
    # Test voice assignment
    print("\nTesting voice assignment...")
    try:
        speakers = audio_service.extract_unique_speakers(scene_script)
        voice_mapping = audio_service.assign_voices_to_speakers(speakers)
        print(f"Voice mapping: {json.dumps(voice_mapping, indent=2)}")
    except Exception as e:
        print(f"Error in voice assignment: {e}")
    
    # Test direct API call with a sample text
    print("\nTesting direct API call...")
    try:
        test_direct_elevenlabs_api_call(
            "This is a test message.",
            voice_mapping["Narrator"]  # Use the narrator's voice
        )
    except Exception as e:
        print(f"Error in direct API call: {e}")
    
    # Test full script processing
    print("\nTesting complete script processing...")
    try:
        output_file = audio_service.process_article(scene_script)
        print(f"Final audio saved to: {output_file}")
    except Exception as e:
        print(f"Error in script processing: {e}")

if __name__ == "__main__":
    main() 