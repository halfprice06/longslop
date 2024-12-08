import base64
from typing import List, Dict, Set, Literal, Optional
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
from anthropic import Anthropic
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

# Add provider type
ProviderType = Literal["openai", "anthropic"]

def normalize_speaker_name(speaker: str) -> str:
    """
    Normalize speaker names to ensure consistency, handling complex cases like 'Ghost of Miranda's Mother'.
    """
    # First handle special case for narrator
    if speaker.strip().lower() == "narrator":
        return "Narrator"
    
    # Handle the full name as one unit first
    name = speaker.strip()
    
    # Split into words while preserving possessives
    words = []
    current_word = []
    
    for char in name:
        if char == ' ':
            if current_word:
                words.append(''.join(current_word))
                current_word = []
            words.append(char)
        elif char == "'":
            current_word.append(char)
        else:
            current_word.append(char)
    
    if current_word:
        words.append(''.join(current_word))
    
    # Process each word
    normalized_words = []
    for word in words:
        if word == ' ':
            normalized_words.append(word)
        elif word.lower() in ['of', 'the', 'and', 'in', 'on', 'at']:
            normalized_words.append(word.lower())
        else:
            # Handle possessives
            if "'" in word:
                base, possessive = word.split("'", 1)
                if possessive.lower().startswith('s'):
                    normalized_words.append(f"{base.title()}'s")
                else:
                    normalized_words.append(f"{base.title()}'{possessive}")
            else:
                normalized_words.append(word.title())
    
    return ''.join(normalized_words)

class AudioService:
    def __init__(self, provider: ProviderType = "anthropic"):
        print("Initializing AudioService...")
        
        # Initialize LLM clients
        self.provider = provider
        if provider == "openai":
            self.instructor_client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        else:  # anthropic
            self.instructor_client = instructor.from_anthropic(Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")))

        # Initialize ElevenLabs client
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
        
        # Track original names for validation
        original_to_normalized = {}
        
        for paragraph in script.paragraphs:
            for line in paragraph.lines:
                original = line.speaker
                normalized = normalize_speaker_name(original)
                if original not in original_to_normalized:
                    original_to_normalized[original] = normalized
                elif original_to_normalized[original] != normalized:
                    raise ValueError(f"Inconsistent speaker name normalization. '{original}' was normalized differently in different places: '{original_to_normalized[original]}' vs '{normalized}'")
                speakers.add(normalized)
                # Update the line's speaker to use normalized version
                line.speaker = normalized
        
        print(f"Found {len(speakers)} unique speakers: {speakers}")
        return speakers

    def extract_character_personalities(self, script: SceneScript) -> Dict[str, str]:
        """
        Use the final story script to extract a structured list of characters and their personalities
        by calling the LLM via instructor.

        Returns:
            dict: { "CharacterName": "Personality Description", ... }
        """
        # Get the set of all speakers that need personalities
        all_speakers = self.extract_unique_speakers(script)

        # Combine the entire script into a textual format
        scene_text_lines = []
        for paragraph in script.paragraphs:
            for line in paragraph.lines:
                # Include speaker and text to give full context
                scene_text_lines.append(f"{line.speaker}: {line.text}")

        full_text = "\n".join(scene_text_lines)

        # Define the prompt
        prompt = f"""
You are an expert story analyst who will analyze a scene script and extract detailed personality descriptions for each character, including the Narrator.

Here is the complete list of characters that need personality descriptions:
{sorted(list(all_speakers))}

Script:
{full_text}

Task:
For each character (including the Narrator), provide a detailed personality description based on:
- Their direct speech (how they talk, word choice, tone)
- Actions described about them
- How they interact with others
- For the Narrator, analyze their narrative style and perspective

The Narrator's personality is especially important as it sets the tone for the story.

Return the result as JSON following this schema:

{CharactersPersonalities.schema_json(indent=2)}

Ensure you provide a personality description for EVERY character listed above. Do not skip any characters.
Do not include any extra commentary, only return the JSON result.
        """

        if self.provider == "anthropic":
            response = self.instructor_client.messages.create(
                model="claude-3-5-sonnet-latest",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8000,
                response_model=CharactersPersonalities
            )
        else:  # openai
            response = self.instructor_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o",
                response_model=CharactersPersonalities
            )

        # Convert response to dictionary
        personalities = {cp.character: cp.personality for cp in response.characters}

        # Verify all speakers got personalities
        missing_speakers = all_speakers - set(personalities.keys())
        if missing_speakers:
            raise ValueError(f"LLM failed to provide personalities for these speakers: {missing_speakers}")

        return personalities

    def assign_voices_via_llm(self, speakers: Set[str], character_personalities: Dict[str, str]) -> Dict[str, str]:
        """
        Use the LLM to match each character to the best-fitting voice from the available voices list.
        """
        # Ensure all speakers have personality descriptions
        for speaker in speakers:
            if speaker not in character_personalities:
                character_personalities[speaker] = f"A character named {speaker} in the story"

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
        if self.provider == "anthropic":
            assignments = self.instructor_client.messages.create(
                model="claude-3-5-sonnet-latest",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8000,
                response_model=VoiceAssignmentResult
            )
        else:  # openai
            assignments = self.instructor_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o",
                response_model=VoiceAssignmentResult
            )

        # Convert assignments to voice mapping dictionary
        voice_mapping = {
            assignment.character: assignment.chosen_voice_id 
            for assignment in assignments.assignments
        }
        
        return voice_mapping

    def validate_voice_assignments(self, voice_mapping: Dict[str, str], speakers: Set[str]) -> None:
        """Validate that all speakers have voice assignments and no extra characters have assignments."""
        # Check that all speakers have voice assignments
        missing_speakers = speakers - set(voice_mapping.keys())
        if missing_speakers:
            raise ValueError(f"Missing voice assignments for speakers: {missing_speakers}")
        
        # Check that there are no extra characters with voice assignments
        extra_characters = set(voice_mapping.keys()) - speakers
        if extra_characters:
            raise ValueError(f"Found voice assignments for non-existent speakers: {extra_characters}")

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

        # Validate voice assignments match speakers exactly
        self.validate_voice_assignments(voice_mapping, speakers)

        self.voice_mapping = voice_mapping
        return self.voice_mapping

    def generate_audio_for_text(self, text: str, voice_id: str) -> Optional[bytes]:
        """
        Generate audio for a single piece of text using ElevenLabs TTS API.
        Returns None if generation fails.
        """
        try:
            print(f"Generating audio for text (length: {len(text)}) with voice ID: {voice_id}")
            # Get the generator from the API
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=text,
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True
                )
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
            print(f"Warning: Failed to generate audio for text: '{text[:100]}...' with voice {voice_id}. Error: {str(e)}")
            return None

    def process_article(self, script: SceneScript) -> str:
        """Main function to process entire script and generate full audio. Returns the filename."""
        print("Processing script...")
        
        # 1. Get unique speakers (now using normalized names)
        speakers = self.extract_unique_speakers(script)
        print(f"Found {len(speakers)} unique speakers: {speakers}")
        
        # 2. Assign voices to speakers using personalities extracted from the script
        voice_mapping = self.assign_voices_to_speakers(speakers, script)
        
        # 3. Generate audio segments
        print("Starting audio generation...")
        audio_segments = []
        failed_segments = []
        
        # Add title narration
        title_audio = self.generate_audio_for_text(script.scene_title, voice_mapping.get("Narrator", self.available_voices[0].voice_id))
        if title_audio:
            audio_segments.append(title_audio)
        else:
            failed_segments.append(("Title", script.scene_title))
        
        # Process each line
        for paragraph in script.paragraphs:
            for line in paragraph.lines:
                voice_id = voice_mapping.get(line.speaker)
                if not voice_id:
                    print(f"Warning: No voice mapping found for speaker: {line.speaker}")
                    failed_segments.append((line.speaker, line.text))
                    continue
                
                audio = self.generate_audio_for_text(line.text, voice_id)
                if audio:
                    audio_segments.append(audio)
                else:
                    failed_segments.append((line.speaker, line.text))
        
        if not audio_segments:
            raise ValueError("No audio segments were successfully generated")
        
        # Report failed segments
        if failed_segments:
            print("\nWarning: The following segments failed to generate:")
            for speaker, text in failed_segments:
                print(f"- {speaker}: {text[:100]}...")
        
        # Combine audio segments
        print(f"\nCombining {len(audio_segments)} audio segments...")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_files = []
                
                # Write each segment to a temporary file
                for i, segment in enumerate(audio_segments):
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
                
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                final_filename = f"audio_{timestamp}.mp3"
                final_path = os.path.join(self.output_dir, final_filename)
                
                # Copy the combined file to the output directory
                with open(output_path, "rb") as src, open(final_path, "wb") as dst:
                    dst.write(src.read())
                
                print(f"Successfully created audio file: {final_filename}")
                return final_filename
                
        except Exception as e:
            raise ValueError(f"Failed to combine audio segments: {str(e)}")