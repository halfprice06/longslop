import base64
from typing import List, Dict, Set
import os
from openai import OpenAI
from app.schemas import SceneLine, Scene, WrittenArticle
import dotenv

dotenv.load_dotenv()

class AudioService:
    def __init__(self):
        self.voice_mapping: Dict[str, str] = {}  # Maps speakers to voice IDs
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize OpenAI client
        
    def extract_unique_speakers(self, article: WrittenArticle) -> Set[str]:
        """Extract all unique speakers from the article, including the narrator."""
        speakers = set()
        speakers.add("narrator")  # Always include narrator
        
        if article.length == "short":
            content = article.content
            for scene in content.scenes:
                if hasattr(scene, 'lines'):
                    for line in scene.lines:
                        speakers.add(line.speaker)
                        
        elif article.length == "medium":
            content = article.content
            # Process intro paragraphs
            for scene in content.intro_paragraphs:
                if hasattr(scene, 'lines'):
                    for line in scene.lines:
                        speakers.add(line.speaker)
            
            # Process main headings
            for heading in content.main_headings:
                for scene in heading.scenes:
                    if hasattr(scene, 'lines'):
                        for line in scene.lines:
                            speakers.add(line.speaker)
                            
            # Process conclusion paragraphs
            for scene in content.conclusion_paragraphs:
                if hasattr(scene, 'lines'):
                    for line in scene.lines:
                        speakers.add(line.speaker)
                        
        elif article.length == "long":
            content = article.content
            # Process main headings and their subheadings
            for heading in content.main_headings:
                for scene in heading.scenes:
                    if hasattr(scene, 'lines'):
                        for line in scene.lines:
                            speakers.add(line.speaker)
                
                # Process subheadings
                for subheading in heading.sub_headings:
                    for scene in subheading.scenes:
                        if hasattr(scene, 'lines'):
                            for line in scene.lines:
                                speakers.add(line.speaker)
                    
                    # Process sub-subheadings
                    for subsubheading in subheading.sub_headings:
                        for scene in subsubheading.scenes:
                            if hasattr(scene, 'lines'):
                                for line in scene.lines:
                                    speakers.add(line.speaker)
        
        return speakers
        
    def assign_voices_to_speakers(self, speakers: Set[str]) -> Dict[str, str]:
        """Assign a unique voice ID to each speaker."""
        # OpenAI currently supports these voices: alloy, echo, fable, onyx, nova, and shimmer
        available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        
        # Always assign 'alloy' to narrator for consistency
        self.voice_mapping["narrator"] = "alloy"
        
        # Assign remaining voices to speakers
        remaining_speakers = speakers - {"narrator"}
        for i, speaker in enumerate(remaining_speakers):
            voice_idx = (i % (len(available_voices) - 1)) + 1  # Skip 'alloy' as it's for narrator
            self.voice_mapping[speaker] = available_voices[voice_idx]
            
        return self.voice_mapping
    
    def generate_audio_for_text(self, text: str, voice_id: str) -> bytes:
        """Generate audio for a single piece of text using OpenAI's text-to-speech."""
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-audio-preview",
                modalities=["text", "audio"],
                audio={"voice": voice_id, "format": "wav"},
                messages=[
                    {
                        "role": "user",
                        "content": f"You are narrating an audiobook. Read the following text: {text}"
                    }
                ]
            )
            
            # Decode the base64 audio data
            wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
            return wav_bytes
            
        except Exception as e:
            print(f"Error generating audio for text: {e}")
            return b""  # Return empty bytes on error
    
    def stitch_audio_segments(self, audio_segments: List[bytes]) -> bytes:
        """Combine multiple audio segments into a single audio file."""
        # For now, we'll just concatenate the WAV files
        # In a production environment, you'd want to use a proper audio library
        # to handle transitions and ensure consistent audio properties
        combined_audio = b"".join(audio_segments)
        return combined_audio
    
    def process_article(self, article: WrittenArticle) -> bytes:
        """Main function to process entire article and generate full audio."""
        # 1. Get unique speakers
        speakers = self.extract_unique_speakers(article)
        
        # 2. Assign voices to speakers
        self.assign_voices_to_speakers(speakers)
        
        # 3. Generate audio segments
        audio_segments = []
        
        def process_scene(scene: Scene):
            if hasattr(scene, 'lines'):
                for line in scene.lines:
                    voice_id = self.voice_mapping[line.speaker]
                    audio = self.generate_audio_for_text(line.text, voice_id)
                    audio_segments.append(audio)
            elif scene.text:  # Narration
                voice_id = self.voice_mapping["narrator"]
                audio = self.generate_audio_for_text(scene.text, voice_id)
                audio_segments.append(audio)
        
        content = article.content
        if article.length == "short":
            for scene in content.scenes:
                process_scene(scene)
                
        elif article.length == "medium":
            # Process intro
            for scene in content.intro_paragraphs:
                process_scene(scene)
            
            # Process main headings
            for heading in content.main_headings:
                # Add heading title as narration
                audio = self.generate_audio_for_text(heading.title, self.voice_mapping["narrator"])
                audio_segments.append(audio)
                
                for scene in heading.scenes:
                    process_scene(scene)
            
            # Process conclusion
            for scene in content.conclusion_paragraphs:
                process_scene(scene)
                
        elif article.length == "long":
            # Process intro paragraphs as narration
            for para in content.intro_paragraphs:
                audio = self.generate_audio_for_text(para, self.voice_mapping["narrator"])
                audio_segments.append(audio)
            
            # Process main headings
            for heading in content.main_headings:
                # Add heading title as narration
                audio = self.generate_audio_for_text(heading.title, self.voice_mapping["narrator"])
                audio_segments.append(audio)
                
                for scene in heading.scenes:
                    process_scene(scene)
                
                # Process subheadings
                for subheading in heading.sub_headings:
                    # Add subheading title as narration
                    audio = self.generate_audio_for_text(subheading.title, self.voice_mapping["narrator"])
                    audio_segments.append(audio)
                    
                    for scene in subheading.scenes:
                        process_scene(scene)
                    
                    # Process sub-subheadings
                    for subsubheading in subheading.sub_headings:
                        # Add sub-subheading title as narration
                        audio = self.generate_audio_for_text(subsubheading.title, self.voice_mapping["narrator"])
                        audio_segments.append(audio)
                        
                        for scene in subsubheading.scenes:
                            process_scene(scene)
            
            # Process conclusion paragraphs as narration
            for para in content.conclusion_paragraphs:
                audio = self.generate_audio_for_text(para, self.voice_mapping["narrator"])
                audio_segments.append(audio)
        
        # 4. Stitch together all segments
        final_audio = self.stitch_audio_segments(audio_segments)
        
        return final_audio 