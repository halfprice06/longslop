import base64
from typing import List, Dict, Set
import os
import json
import uuid
from datetime import datetime
import io
import tempfile
import requests
import logging

import dotenv
from openai import OpenAI
import instructor
from elevenlabs import ElevenLabs, VoiceSettings

from app.schemas import (
    SceneLine, 
    SceneScript, 
    VoiceOption, 
    VoiceAssignmentResult, 
    CharacterVoiceAssignment,
    CharacterPersonality,
    CharactersPersonalities
)

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

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

        # Initialize instructor client
        self.instructor_client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))

        print("Initializing AudioService...")
        self.voice_mapping: Dict[str, str] = {}  # Maps speakers to voice IDs
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

        # Define available voices with IDs and descriptions
        # Note: Replace with actual voice descriptions from ElevenLabs
        self.available_voices: List[VoiceOption] = [
            VoiceOption(voice_id="WWr4C8ld745zI3BiA8n7", name="Robert Riggs", description="American male baritone voice with an authoritative low pitched voice. His melodious voice sounds trustworthy and produces a calming effect while telling stories about intense subjects."),
            VoiceOption(voice_id="fCxG8OHm4STbIsWe4aT9", name="Harrison Gale", description="A voice imbued with a deep, velvety richness that commands attention and soothes the listener - not only sonorous and authoritative but also carries a charismatic allure, making it perfect for a wide array of projects from immersive audiobooks and engaging advertisements to compelling documentaries and educational content - blends a classical baritone depth with a modern clarity, ideal for bringing narratives to life or lending gravitas to commercial ventures."),
            VoiceOption(voice_id="jB108zg64sTcu1kCbN9L", name="Zeus Epic", description="Deep, Confident, Authoritative type - slight raspy "),
            VoiceOption(voice_id="bU2VfAdiOb2Gv2eZWlFq", name="CarterSutra", description="Young American male voice. Smooth as a molten stream of molasses, slow and languid, drawing you in with its sultry cadence, each syllable a delicious indulgence that lingered on the lips."),
            VoiceOption(voice_id="NFG5qt843uXKj4pFvR7C", name="Adam Stone", description="A middle aged 'Brit' with a velvety laid back, late night talk show host timbre."),
            VoiceOption(voice_id="7Uw4vgM4Qb1qiwwUnu15", name="Soothing Sam", description="An intimate, smooth voice recorded with a high-end microphone and top tier audio engineering. Suitable for Narration."),
            VoiceOption(voice_id="jMFz7MY1ukKGAVcx8vKI", name="Mauricio - Hispanic", description="A warm and polite young man with a soft Latin-Hispanic English accent. Ideal for presentations, voice over videos and educational content."),
            VoiceOption(voice_id="XrExE9yKIg1WjnnlVkGX", name="Matilda", description="Average female american voice."),
            VoiceOption(voice_id="dAcds2QMcvmv86jQMC3Y", name="Jayce", description="A full-bodied, bassy, slightly raspy and rough voice with a UK accent."),
            VoiceOption(voice_id="f2yUVfK5jdm78zlpcZ8C", name="Albert - Funny Cartoon Character", description="Young German male with a strongly dynamic voice. Works perfectly for funny, nerdy and silly characters. Absolutely hilarious."),
            VoiceOption(voice_id="chcMmmtY1cmQh2ye1oXi", name="Timmy", description="A young to middle aged medieval style character. High energy, Higher Pitch. Perfect for Games & Animation. Peasant, Unit, Grunt, Villager, Town Crier, Farmer."),
            VoiceOption(voice_id="BL7YSL1bAkmW8U0JnU8o", name="Jen - Soothing Gentle Thoughtful Melancholy", description="A calm, somber, thoughtful, reflective, velvety, melancholy voice with mid-deep tones. Good for poetry, meditation, and narration. "),
            VoiceOption(voice_id="A9evEp8yGjv4c3WsIKuY", name="Ralf Eisend", description="An international audio book speaker with clear and deep voice, ideal for audio books and audibles."),
            VoiceOption(voice_id="7NsaqHdLuKNFvEfjpUno", name="Seer Morganna", description="The voice of an old wise seer woman telling people of their fortunes. Works well for Animations and characters in a story."),
            VoiceOption(voice_id="pBZVCk298iJlHAcHQwLr", name="Leoni Vergara", description="International Cosmopolitan and educated voice. Warm, soothing, friendly and eloquent tone.  Works great for Virtual Assistants and conversational text."),
            VoiceOption(voice_id="YXpFCvM1S3JbWEJhoskW", name="Wyatt- Wise Rustic Cowboy", description="Weathered wisdom from a Cowboy who's lived a hard life on the range.  An older American Deep Male voice with a Southern flavor.  Excellent for reading stories of the Wild West or American history.  "),
            VoiceOption(voice_id="M0IvLNu6hH3cNnETNLEP", name="Lucas Reed - Expressive & Dramatic North American", description="Lucas Reed’s voice captivates with dynamic expression, warmth, wit, and sophistication. Perfect for dramatic storytelling, character performances, ads, or monologues, his versatile North American tones stand out. Trained on recordings rich in emotion, his range also features non-verbals like laughter, gasps, and sighs."),
            VoiceOption(voice_id="KTPVrSVAEUSJRClDzBw7", name="Cowboy Bob // VF", description="An aged American male voice, rich with the gravel of countless tales and tinged with a Southern drawl as comforting as a porch swing at dusk. It carries the wisdom of the Old West and the warmth of a sunset over the plains, perfect for stories needing a touch of rugged charm and timeless wisdom."),
            VoiceOption(voice_id="eVItLK1UvXctxuaRV2Oq", name="Sexy Female Villain Voice", description="A seductive and dangerous femme fatale, this female voice drips with the sexy allure of a villain. Perfect for video game characters. Think over the top, exaggerated, anime villain voice!"),
            VoiceOption(voice_id="flHkNRp1BlvT73UL6gyz", name="Jessica Anne Bogart", description="Female villain! Wickedly eloquent. Calculating. Cruel and calm."),
            VoiceOption(voice_id="uVKHymY7OYMd6OailpG5", name="Frederick - Old Gnarly Narrator", description="Listen to the rugged tales, this grizzled baritone tells. This gnarly, well-seasoned voice rings with hard-won authenticity and wisdom, ideal for historical epics, gritty westerns, and stories demanding a road-worn raconteur. Hewn from decades of hard-lived adventures, his timbre captivates with a richly textured tapestry of human experience. Immerse yourself in the soulful perseverance and existential gravitas evoked by his masterfully aged, craggy vocals."),

        ]

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

    def extract_character_personalities(self, script: SceneScript) -> Dict[str, str]:
        """
        Use the final story script to extract a structured list of characters and their personalities
        by calling the LLM via instructor.

        Returns:
            dict: { "CharacterName": "Personality Description", ... }
        """

        # Combine the entire script into a textual format
        # We'll just feed all lines to the prompt
        scene_text_lines = []
        for paragraph in script.paragraphs:
            for line in paragraph.lines:
                # Include speaker and text to give full context
                scene_text_lines.append(f"{line.speaker}: {line.text}")

        full_text = "\n".join(scene_text_lines)

        # Define the prompt
        prompt = f"""
You are an assistant who will analyze a scene script and extract a brief personality description of each character.

Script:
{full_text}

Task:
Identify all distinct characters (excluding "Narrator" if present) and provide a short personality description for each. The description should capture their essence based on how they speak or act in the scene.

Return the result as JSON following this schema:

{CharactersPersonalities.schema_json(indent=2)}

Do not include any extra commentary, only return the JSON result.
        """

        response = self.instructor_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o",
            response_model=CharactersPersonalities
        )

        # response is now a CharactersPersonalities object
        personalities = {cp.character: cp.personality for cp in response.characters}

        # Always include the Narrator if not assigned
        if "Narrator" not in personalities:
            personalities["Narrator"] = "A neutral, omniscient observer who narrates events calmly."

        return personalities

    def assign_voices_via_llm(self, speakers: Set[str], character_personalities: Dict[str, str]) -> Dict[str, str]:
        """
        Use the LLM to match each character to the best-fitting voice from the available voices list.
        """
        voices_list = [v.model_dump() for v in self.available_voices]

        prompt = f"""
You are an expert casting director who chooses voices for characters based on their personality descriptions.

Below is a list of available voices with their IDs, names, and descriptions:

{json.dumps(voices_list, indent=2)}

Below is a list of characters and their personality descriptions:
{json.dumps(character_personalities, indent=2)}

Task:
Assign the best voice_id for each character from the provided voices. Each character gets exactly one voice_id.

Return the result as JSON following this schema:

{VoiceAssignmentResult.schema_json(indent=2)}

Do not include any extra commentary, only return the JSON result.
        """

        # Call instructor to parse the response as VoiceAssignmentResult
        assignments = self.instructor_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o",
            response_model=VoiceAssignmentResult
        )

        voice_mapping = {a.character: a.chosen_voice_id for a in assignments.assignments}
        return voice_mapping

    def assign_voices_to_speakers(self, speakers: Set[str], script: SceneScript) -> Dict[str, str]:
        """
        Assign voices using the LLM-based assignment. 
        Extract character personalities from the final script first.
        """
        character_personalities = self.extract_character_personalities(script)

        # Ensure narrator personality
        if "Narrator" not in character_personalities:
            character_personalities["Narrator"] = "A neutral, omniscient observer who narrates the story calmly."

        # If no narrator in speakers, just assign all
        if "Narrator" not in speakers:
            voice_mapping = self.assign_voices_via_llm(speakers, character_personalities)
        else:
            # Assign narrator a default voice directly or let LLM do it as well
            # Here we let LLM handle narrator too, or we can do a special case
            voice_mapping = self.assign_voices_via_llm(speakers, character_personalities)

        self.voice_mapping = voice_mapping
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
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
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
        
        # 2. Assign voices to speakers using personalities extracted from the script
        voice_mapping = self.assign_voices_to_speakers(speakers, script)
        
        # 3. Generate audio segments
        print("Starting audio generation...")
        audio_segments = []
        
        # Add title narration
        title_audio = self.generate_audio_for_text(script.scene_title, voice_mapping.get("Narrator", self.available_voices[0].voice_id))
        if title_audio:
            audio_segments.append(title_audio)
        
        # Process each paragraph
        for paragraph in script.paragraphs:
            for line in paragraph.lines:
                voice_id = voice_mapping[line.speaker]  # Use assigned voices
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