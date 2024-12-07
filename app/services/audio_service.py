import base64
from typing import List, Dict, Set
import os
from elevenlabs import ElevenLabs, VoiceSettings
from app.schemas import SceneLine, SceneScript
import dotenv
import uuid
from datetime import datetime
import io
import tempfile

dotenv.load_dotenv()

def normalize_speaker_name(speaker: str) -> str:
    """Normalize speaker names to ensure consistency."""
    # Convert to title case first
    normalized = speaker.strip().title()
    
    # Special case for narrator - always capitalize
    if normalized.lower() == "narrator":
        return "Narrator"
        
    return normalized

class AudioService:
    def __init__(self):
        print("Initializing AudioService...")
        self.voice_mapping: Dict[str, str] = {}  # Maps speakers to voice IDs
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        # Create frontend/output directory if it doesn't exist
        self.output_dir = os.path.join("frontend", "output")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        print("AudioService initialized successfully")
        
    def extract_unique_speakers(self, script: SceneScript) -> Set[str]:
        """Extract all unique speakers from the script."""
        print("Extracting speakers from script...")
        speakers = set()
        speakers.add("Narrator")  # Always include narrator with correct capitalization
        
        for paragraph in script.paragraphs:
            for line in paragraph.lines:
                speakers.add(normalize_speaker_name(line.speaker))
        
        print(f"Found {len(speakers)} unique speakers: {speakers}")
        return speakers
        
    def assign_voices_to_speakers(self, speakers: Set[str]) -> Dict[str, str]:
        """Assign a unique voice ID to each speaker."""
        print("Assigning voices to speakers...")
        # TODO: Replace with actual ElevenLabs voice IDs
        available_voices = [
            "uVKHymY7OYMd6OailpG5",  # Default voice ID for now
            "eVItLK1UvXctxuaRV2Oq",  # Add more voice IDs here
            "flHkNRp1BlvT73UL6gyz",
            "FF7KdobWPaiR0vkcALHF",
            "qNkzaJoHLLdpvgh5tISm"
        ]
        
        # Always assign first voice to narrator for consistency
        self.voice_mapping["Narrator"] = available_voices[0]
        print(f"Assigned voice ID '{available_voices[0]}' to Narrator")
        
        # Assign remaining voices to speakers
        remaining_speakers = speakers - {"Narrator"}
        for i, speaker in enumerate(remaining_speakers):
            voice_idx = (i % (len(available_voices) - 1)) + 1
            self.voice_mapping[speaker] = available_voices[voice_idx]
            print(f"Assigned voice ID '{available_voices[voice_idx]}' to speaker '{speaker}'")
            
        return self.voice_mapping
    
    def generate_audio_for_text(self, text: str, voice_id: str) -> bytes:
        """Generate audio for a single piece of text using ElevenLabs TTS API."""
        print(f"Generating audio for text (length: {len(text)}) with voice ID: {voice_id}")
        try:
            # Get the generator from the API
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=text,
                output_format="mp3_44100_128",
                settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True)
            )
            
            # Convert generator to bytes by reading all chunks
            audio_chunks = []
            for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)
            
            # Combine all chunks into a single bytes object
            audio_data = b''.join(audio_chunks)
            print(f"Successfully generated audio segment of size: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            print(f"Error generating audio for text: {e}")
            return b""  # Return empty bytes on error
    
    def stitch_audio_segments(self, audio_segments: List[bytes]) -> bytes:
        """Combine multiple audio segments into a single MP3 file."""
        print(f"Stitching {len(audio_segments)} audio segments together...")
        
        if not audio_segments:
            return b""

        # Create a temporary directory to store individual segments
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save each segment to a temporary file
            temp_files = []
            for i, segment in enumerate(audio_segments):
                if segment:  # Only process non-empty segments
                    temp_path = os.path.join(temp_dir, f"segment_{i}.mp3")
                    with open(temp_path, "wb") as f:
                        f.write(segment)
                    temp_files.append(temp_path)
            
            # Use ffmpeg to concatenate MP3 files
            output_path = os.path.join(temp_dir, "output.mp3")
            concat_list = os.path.join(temp_dir, "concat.txt")
            
            # Create concat file for ffmpeg
            with open(concat_list, "w") as f:
                for temp_file in temp_files:
                    f.write(f"file '{temp_file}'\n")
            
            # Run ffmpeg
            os.system(f'ffmpeg -f concat -safe 0 -i "{concat_list}" -c copy "{output_path}"')
            
            # Read the final output
            with open(output_path, "rb") as f:
                combined_audio = f.read()
        
        print(f"Final audio size: {len(combined_audio)} bytes")
        return combined_audio

    def process_article(self, script: SceneScript) -> str:
        """Main function to process entire script and generate full audio. Returns the filename."""
        print("Processing script...")
        
        # Normalize all speaker names in the script
        for paragraph in script.paragraphs:
            for line in paragraph.lines:
                line.speaker = normalize_speaker_name(line.speaker)
        
        # 1. Get unique speakers (now using normalized names)
        speakers = self.extract_unique_speakers(script)
        
        # 2. Assign voices to speakers
        self.assign_voices_to_speakers(speakers)
        
        # 3. Generate audio segments
        print("Starting audio generation...")
        audio_segments = []
        
        # Add title narration
        title_audio = self.generate_audio_for_text(script.scene_title, self.voice_mapping["Narrator"])
        if title_audio:
            audio_segments.append(title_audio)
        
        # Process each paragraph
        for paragraph in script.paragraphs:
            for line in paragraph.lines:
                voice_id = self.voice_mapping[line.speaker]  # Will now use normalized speaker names
                print(f"Processing line for speaker '{line.speaker}' with voice '{voice_id}'")
                audio = self.generate_audio_for_text(line.text, voice_id)
                if audio:  # Only append if we got valid audio
                    audio_segments.append(audio)
        
        # 4. Stitch together all segments
        print("Finalizing audio processing...")
        final_audio = self.stitch_audio_segments(audio_segments)
        
        # 5. Save to file with unique name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"story_{timestamp}_{unique_id}.mp3"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(final_audio)
        
        print(f"Script processing complete. Saved to {filepath}")
        return filename