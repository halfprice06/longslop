# Python standard library imports
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

# Third-party imports
from anthropic import Anthropic
from dotenv import load_dotenv
import openai
import instructor

# Local imports
from app.constants.forbidden_words import FORBIDDEN_WORDS
from app.constants.writing_styles import AVAILABLE_STYLES
from app.database import ArticleDB
from app.schemas import (
    ArticleLength,
    ArticleStructure,
    LongArticleStructure,
    MediumArticleStructure,
    ShortArticleStructure,
    Paragraph
)

# Initialize the database
db = ArticleDB()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the project root directory (where .env should be)
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

logger.info(f"Looking for .env file at: {env_path}")

# Load environment variables
load_dotenv(env_path)

# Set the API key directly
api_key = os.getenv("OPENAI_API_KEY")

# Set the API key directly on the openai module
openai.api_key = api_key

# After the existing logging setup
if os.getenv('DEBUG', 'false').lower() == 'true':
    logger.setLevel(logging.DEBUG)

# Add Anthropic client initialization after OpenAI client
anthropic_instructor_client = instructor.from_anthropic(Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
))

anthropic_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


# Add provider type
ProviderType = Literal["openai", "anthropic"]


def check_forbidden_words(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text contains any forbidden words or their variations.
    Returns (has_forbidden, found_words)
    """
    found_words = []
    text_lower = text.lower()
    
    # Word boundary patterns for each type of word
    for word in FORBIDDEN_WORDS:
        # Create regex pattern based on word type
        if word.endswith('e'):
            # For words ending in 'e' (showcase, underscore, etc)
            # Match: showcase, showcased, showcasing
            pattern = fr'\b{word}[ds]?\b|\b{word[:-1]}ing\b'
        elif ' ' in word:
            # For phrases, match exactly
            pattern = fr'\b{re.escape(word)}\b'
        else:
            # For other words, match common variations
            # Match: word, words, worded, wording
            pattern = fr'\b{word}(?:s|ed|ing)?\b'
            
        if re.search(pattern, text_lower):
            found_words.append(word)
            
    return bool(found_words), found_words

def log_api_error(function_name: str, error: Exception, **extra_info):
    """Helper function to log API errors with detailed information"""
    error_details = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'function': function_name,
        **extra_info
    }
    logger.error(f"API Error Details: {error_details}", exc_info=True)

def test_api_connection():
    """Test the OpenAI API connection"""
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {"role": "user", "content": "Say hello"}
            ]
        )
        logger.info("API connection test successful")
        return True
    except Exception as e:
        log_api_error('test_api_connection', e, model="gpt-4o-2024-11-20")
        return False

def generate_article_plan(
    topic: str, 
    style_name: str = "new_yorker", 
    length: Union[str, ArticleLength] = ArticleLength.LONG,
    provider: ProviderType = "openai"
) -> str:
    """Generate initial brainstorming and planning for the article"""
    try:
        # Convert length to ArticleLength enum if it's a string
        if isinstance(length, str):
            length = ArticleLength(length.lower())
            
        # Test API connection first
        if not test_api_connection():
            raise Exception("Failed to connect to OpenAI API")
            
        # Get style details
        style = AVAILABLE_STYLES.get(style_name.lower(), AVAILABLE_STYLES["new_yorker"])
        
        # Define length-specific instructions
        length_instructions = {
            ArticleLength.SHORT: """
Plan a concise article or short story around 500-1000 words.
The piece should have a clear and impactful point or theme.
                """,
                ArticleLength.MEDIUM: """
Plan a medium-length article or short story of approximately 1000-2000 words.
For articles, include 2-3 main sections that build your argument.
For short stories, outline key plot points with character development.
Ensure each section or plot point flows naturally into the next.
                """,
                ArticleLength.LONG: """
Plan a comprehensive longform article or short story of 2000+ words.
For articles, include 3-5 main sections with potential subsections for detailed analysis.
For short stories, develop a complex narrative with multiple characters, subplots, and detailed exploration of themes.
Allow space for in-depth exploration of ideas or intricate storytelling elements. Describe specific scenes in the order they occur.
                """
            }
        
        logger.info(f"Generating {length.value} article plan for topic: {topic} in {style.name} style using {provider}")
        
        prompt = f"""You are an expert article or short story planner for {style.name}. You are planning a {length.value} article or short story that matches their distinctive style and editorial approach.

        Style Description: {style.description}

        Example of the style:
        {style.example}

        Length Requirements:
        {length_instructions[length]}

        Create a detailed plan for an article or short story about: {topic}
        
        Your suggested article title or short story title should match {style.name}'s style perfectly. Consider these characteristics for titles:

        A world class short story should feature the following:

        - Strong Theme

        Every element of the story must tie back to the central theme
        Must be succinct and focused - no room for ambiguity
        Theme acts as a container that holds all elements together
        Needs to be memorable

        - Complete Plot

        Must have beginning, middle, and end
        Should include a character arc
        Keep it simple - focus on one main idea
        Must be plausible and logical, even in fantastical settings
        Can use traditional story structures like three-act format


        - Focused Climax - THIS IS THE MOST IMPORTANT PART

        Everything must lead to the climax
        Every word and element should work toward this destination
        Should be UNEXPECTED yet INEVITABLE, A TWIST, SOMETHING THE READER WON'T SOON FORGET
        Once reached, the story ends
        No room for subplots or digressions

        - Human Connection

        Must explore some aspect of the human condition
        Should matter to both writer and reader
        Needs to touch on real human experiences and emotions
        Must be genuinely felt, not "faked"
        Should be relatable even if writing about non-human subjects

        - Originality

        Must be fresh and original
        Can't rely on clichés
        Short story readers expect higher standards
        Even when using tropes, should present them in new ways

        Plan the article or short story to fully embrace {style.name}'s distinctive voice and approach throughout.

        For short stories, make sure there is enough action and dialogue to keep the reader engaged. Describe every scene in great detail.

        Make sure in every scene you have completely anazlyed the characters and their motivations and specifically plan why they are taking specific actions. Think long term about the whole story when planning.

        Make sure to bias each scene to contain a lot of character actions or dialogue. We don't want the story to drag. 
        """

        if provider == "anthropic":
            completion = anthropic_client.messages.create(
                model="claude-3-5-sonnet-latest",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=8000
            )
            output_text = completion.content[0].text.strip()
        else:
            completion = openai.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            output_text = completion.choices[0].message.content.strip()

        # Log the input prompt and output text
        db.save_llm_call_log(
            prompt, 
            output_text
        )

        return output_text

    except Exception as e:
        log_api_error('generate_article_plan', e, 
                     topic=topic, 
                     style=style_name, 
                     length=length.value,
                     provider=provider)
        raise Exception(f"Failed to generate article plan: {str(e)}")

def structure_article_plan(plan: str, length: ArticleLength = ArticleLength.LONG, provider: ProviderType = "openai") -> ArticleStructure:
    """Convert the narrative plan into a structured article outline"""
    try:
        logger.info(f"Converting narrative plan to structured outline with length: {length}")
        
        # Adjust the system prompt based on length
        length_instructions = {
            ArticleLength.SHORT: """Create a simple article or short story structure with just paragraphs - no headings or sections.""",
            ArticleLength.MEDIUM: """Create an article or short story structure with up to 3 main headings. Do not include subheadings.""",
            ArticleLength.LONG: """Create a full article or short story structure with main headings, subheadings, and sub-subheadings."""
        }
        
        # Select the appropriate response format based on length
        response_format = {
            ArticleLength.SHORT: ShortArticleStructure,
            ArticleLength.MEDIUM: MediumArticleStructure,
            ArticleLength.LONG: LongArticleStructure
        }[length]
        
        # Add length guidance to the system prompt
        system_prompt = f"""You are an expert at structuring articles or short stories. 
        
        {length_instructions[length]}

        Convert the given unstructured narrative plan into a structured outline of the given length. 

        You aren't writing content at this stage, you are giving the outline of what each scene or section and paragraph will be about.
        
        For a short article or short story:
        - Just paragraphs, no headings

        For a medium article or short story:
        - Include 2-3 main headings
        - No subheadings
        
        For a long article or short story:
        - Include 3-5 main headings
        - Each main heading can have 2-3 subheadings
        - Each subheading can have 1-2 sub-subheadings
        
        The paragraph description should each represent a specific scene in the story and capture as much detail as possible about what the scene or section is about.

        The 'must include' information should include any specific details or quotes or suggested lines that appear in the narrative plan for a given scene or section, and also details like the characters actions and motivations.

        The paragraphs must cover the entire scope of the article or the plot of the story and include every scene described in the unstructured narrative plan. 
        
        """
        
        # Create the full prompt by combining system prompt and user content
        full_prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": plan}
        ]

        if provider == "anthropic":
            completion = anthropic_instructor_client.messages.create(
                model="claude-3-5-sonnet-latest",
                system=system_prompt,
                messages=[{"role": "user", "content": plan}],
                max_tokens=8000, 
                response_model=response_format
            )

            # The completion is already the parsed model
            structured_content = completion

        else:
            completion = openai.beta.chat.completions.parse(
                model="gpt-4o",
                messages=full_prompt,
                response_format=response_format
            )

            # Handle potential refusal
            if completion.choices[0].message.refusal:
                refusal_msg = completion.choices[0].message.refusal
                logger.warning(f"Model refused to structure plan: {refusal_msg}")
                raise Exception(f"Model refused to structure the article plan: {refusal_msg}")
            
            # Get the parsed response
            structured_content = completion.choices[0].message.parsed

        # Log the output - convert structured_content to dict before saving
        db.save_llm_call_log(
            system_prompt + "\n\n" + plan, 
            structured_content.model_dump()  # Convert to dict before saving
        )

        # Create the final ArticleStructure
        article_structure = ArticleStructure(
            length=length,
            content=structured_content
        )
        
        logger.debug(f"Received structured response: {article_structure.model_dump_json()}")

        return article_structure
    
    except Exception as e:
        log_api_error('structure_article_plan', e, 
                     plan_length=len(plan), 
                     article_length=length,
                     model="gpt-4o")
        raise Exception(f"Failed to structure article plan: {str(e)}")

def critique_and_elaborate_article_plan(
    topic: str,
    original_plan: str,
    structured_plan: ArticleStructure,
    style_name: str = "new_yorker",
    length: ArticleLength = ArticleLength.LONG,
    provider: ProviderType = "openai"
) -> str:
    """Critique and elaborate on the article plan to make it better."""
    try:
        logger.info(f"Critiquing and elaborating on the article plan.")

        style = AVAILABLE_STYLES.get(style_name.lower(), AVAILABLE_STYLES["new_yorker"])

        # Convert the structured plan to text to provide to the LLM
        structured_plan_text = json.dumps(structured_plan.model_dump(), indent=2)

        prompt = f"""
        As an expert editor and planner, please critique and elaborate on the following article or short story plan to improve its structure, coherence, and depth. Provide suggestions to make the article or short story more compelling and comprehensive.

        Original Topic: {topic}

        Original Narrative Plan:
        {original_plan}

        Structured Plan:
        {structured_plan_text}

        Instructions:
        - Identify any weaknesses or gaps in the plan.
        - Suggest improvements or additions to enhance the article or short story.
        - Provide a complete revised narrative plan that incorporates these improvements.

        A world class short story should feature the following:

        - Strong Theme


        Every element of the story must tie back to the central theme
        Must be succinct and focused - no room for ambiguity
        Theme acts as a container that holds all elements together
        Needs to be memorable


        - Complete Plot


        Must have beginning, middle, and end
        Should include a character arc
        Keep it simple - focus on one main idea
        Must be plausible and logical, even in fantastical settings
        Can use traditional story structures like three-act format


        - Focused Climax - THIS IS THE MOST IMPORTANT PART


        Everything must lead to the climax
        Every word and element should work toward this destination
        Should be UNEXPECTED yet INEVITABLE, A TWIST, SOMETHING THE READER WON'T SOON FORGET
        Once reached, the story ends
        No room for subplots or digressions


        - Human Connection


        Must explore some aspect of the human condition
        Should matter to both writer and reader
        Needs to touch on real human experiences and emotions
        Must be genuinely felt, not "faked"
        Should be relatable even if writing about non-human subjects


        - Originality

        Must be fresh and original
        Can't rely on clichés
        Short story readers expect higher standards
        Even when using tropes, should present them in new ways

        Plan the article or short story to fully embrace {style.name}'s distinctive voice and approach throughout.

        For short stories, make sure there is enough action and dialogue to keep the reader engaged. Describe every scene in great detail.

        Make sure in every scene you have completely anazlyed the characters and their motivations and specifically plan why they are taking specific actions. Think long term about the whole story when planning.

        Make sure to bias each scene to contain a lot of character actions or dialogue. We don't want the story to drag. 

        Please return only the revised narrative plan.
        """

        if provider == "anthropic":
            completion = anthropic_client.messages.create(
                model="claude-3-5-sonnet-latest",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=8000
            )
            revised_plan = completion.content[0].text.strip()
        else:
            completion = openai.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=[{"role": "user", "content": prompt}]
            )
            revised_plan = completion.choices[0].message.content.strip()

        # Log the output - convert messages to list before saving
        db.save_llm_call_log(
            prompt,
            revised_plan
        )

        logger.info("Successfully critiqued and elaborated on the article plan.")
        return revised_plan

    except Exception as e:
        log_api_error('critique_and_elaborate_article_plan', e)
        raise Exception(f"Failed to critique and elaborate article plan: {str(e)}")
    

def apply_style_transfer(
    content: str,
    paragraph_description: str,
    must_include: str,
    style_name: str = "new_yorker",
    provider: ProviderType = "openai"
) -> str:
    """Apply style transfer to the generated content, incorporating paragraph_description and must_include."""
    try:
        style = AVAILABLE_STYLES.get(style_name.lower(), AVAILABLE_STYLES["new_yorker"])
        max_retries = 3
        current_try = 0
        all_forbidden_words = set()
        styled_content = content

        while current_try < max_retries:
            try:
                if current_try == 0:
                    # Initial style transfer
                    prompt = f"""Rewrite the following content to match the style of {style.name} writing.

Style Description: {style.description}

Example of the style: {style.example}

Important Rules:

1. Maintain ALL factual information and key points from the original
2. Keep the same basic structure and flow of ideas
3. Only change the writing style and voice
4. Do not add or remove any significant information
5. Preserve any technical accuracy in the original

You may not use any of the following words or phrases: {', '.join(FORBIDDEN_WORDS)}

The rewritten content must:

- Follow the description: {paragraph_description}
- Must include: {must_include}

Original content:

{content}

Rewrite the content in the specified style while keeping all information intact."""
                else:
                    # Retry attempts focus on removing forbidden words
                    prompt = f"""Rewrite the following content as close to verbatim as possible,
maintaining the same narrative flow and key information but eliminating
these forbidden words or phrases: {', '.join(all_forbidden_words)}.

You also may not use any of the following words or phrases: {', '.join(FORBIDDEN_WORDS)} in the rewritten content.

The rewritten content must:

- Follow the description: {paragraph_description}
- Must include: {must_include}

Make sure to bias each scene to contain a lot of character actions or dialogue. We don't want the story to drag. 

Previous version:

{styled_content}

Do not return any content other than the rewritten content. Do not include introductory text like 'Here is the rewritten content:, just return the rewritten text by itself."""

                # Call the LLM API
                if provider == "anthropic":
                    completion = anthropic_client.messages.create(
                        model="claude-3-5-sonnet-latest",
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=8000
                    )
                    styled_content = completion.content[0].text.strip()

                else:
                    completion = openai.chat.completions.create(
                        model="gpt-4o-2024-11-20",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    styled_content = completion.choices[0].message.content.strip()

                # Log the output
                db.save_llm_call_log(prompt, styled_content)

                # Check for forbidden words
                has_forbidden, found_words = check_forbidden_words(styled_content)

                if has_forbidden:
                    all_forbidden_words.update(found_words)
                    current_try += 1
                    logger.warning(f"Style transfer attempt {current_try}: Found forbidden words: {found_words}")
                    if current_try >= max_retries:
                        logger.warning(f"Using content with forbidden words after {max_retries} attempts. Words found: {', '.join(found_words)}")
                        break
                    continue

                # If we get here with no forbidden words, break the loop
                break

            except Exception as api_error:
                log_api_error('apply_style_transfer.api_call', api_error,
                              style=style_name,
                              attempt=current_try)
                current_try += 1
                if current_try >= max_retries:
                    logger.warning("Style transfer failed after all retries, returning original content")
                    return content
                continue

        return styled_content

    except Exception as e:
        log_api_error('apply_style_transfer', e,
                      style=style_name,
                      content_length=len(content))
        logger.warning("Style transfer failed, returning original content")
        return content


def get_section_description(plan: ArticleStructure, path: List[str]) -> str:
    """Get a description of the section we want to write based on the path"""
    if path[0] == "intro":
        return "Write the introduction or exposition paragraphs for the article or short story."
    elif path[0] == "conclusion":
        return "Write the conclusion or resolution paragraphs for the article or short story."
    elif path[0] == "main":
        # Handle different article structures
        if isinstance(plan.content, ShortArticleStructure):
            return "Write the main content paragraphs for the short story. Make sure to cover each paragraph listed in the structured plan in order along with the necessary 'must include' information, while keeping in mind the overall plan for the article or story."
            
        # Navigate to the correct heading/subheading for medium and long articles
        heading_idx = int(path[1])
        heading = plan.content.main_headings[heading_idx]
        
        if len(path) == 2:
            return f"Write the content for the main heading: {heading.title}. Make sure to cover each paragraph listed in the structured plan in order, along with the necessary 'must include' information, while keeping in mind the overall plan for the article or story."
        
        if path[2] == "sub":
            # Only process subheadings for LongArticleStructure
            if not isinstance(plan.content, LongArticleStructure):
                raise ValueError("Subheadings are only available in long articles")
                
            sub_idx = int(path[3])
            subheading = heading.sub_headings[sub_idx]
            
            if len(path) == 4:
                return f"Write the content for the subheading: {subheading.title}. Make sure to cover each paragraph listed in the structured plan in order, along with the necessary 'must include' information, while keeping in mind the overall plan for the article or story."
            
            if path[4] == "subsub":
                subsub_idx = int(path[5])
                subsubheading = subheading.sub_headings[subsub_idx]
                return f"Write the content for the sub-subheading: {subsubheading.title}. Make sure to cover each paragraph listed in the structured plan in order, along with the necessary 'must include' information, while keeping in mind the overall plan for the article or story."
    
    raise ValueError(f"Invalid section path: {path}")

# # Modify the write_section function to include style transfer
# def write_section(
#     topic: str,
#     original_plan: str,
#     structured_plan: ArticleStructure,
#     written_content: ArticleStructure,
#     section_path: List[str],
#     style: str = "new_yorker",
#     provider: ProviderType = "openai"
# ) -> List[str]:
#     """Write a specific section of the article or short story."""
#     try:
#         # Format the content that's been written so far
#         formatted_content = format_written_content(written_content.content)
        
#         # Get the section description based on the structure type
#         section_desc = get_section_description(structured_plan, section_path)
        
#         logger.info(f"Writing section with path: {section_path}")

#         logger.debug(f"Section description: {section_desc}")
        
#         # Get the selected style details
#         style_details = AVAILABLE_STYLES.get(style.lower(), AVAILABLE_STYLES["new_yorker"])
        
#         try:
#             prompt = f"""
#             <style guide> 
            
#             You are an expert authoer writing in the style of {style_details.name}.
            
#             Style Description: {style_details.description}
            
#             Example of the style:
#             {style_details.example}

#             You may not use any of the following words or phrases: {', '.join(FORBIDDEN_WORDS)}

#             Write in clear, distinct paragraphs.

#             Do not include any headers, but you may use markdown to apply bolding, italics, and underlining.
            
#             </style guide>             
            
#             <instructions>

#             Write the next (or sometimes first)section of the article or short story, maintaining consistency with previously written content and the overall plan.

#             Original Topic: 
            
#             {topic}
            
#             Original Plan: 
            
#             {original_plan}

#             Structured Plan for the Article or Short Story: 
            
#             {structured_plan.model_dump_json()}

#             Content Written So Far:

#             {formatted_content}

#             Please write the following section:

#             {section_desc}

#             """

#             if provider == "anthropic":
#                 completion = anthropic_client.messages.create(
#                     model="claude-3-5-sonnet-latest",
#                     messages=[
#                         {"role": "user", "content": prompt}
#                     ], 
#                     max_tokens=8000
#                 )
#                 generated_content = completion.content[0].text.strip()
#             else:
#                 completion = openai.chat.completions.create(
#                     model="gpt-4o-2024-11-20",
#                     messages=[{"role": "user", "content": prompt}],
#                 )
#                 generated_content = completion.choices[0].message.content.strip()
            
#             # Log the output
#             db.save_llm_call_log(
#                 [{"role": "user", "content": prompt}], 
#                 generated_content
#             )

#             # Apply style transfer (which now handles forbidden words)
#             styled_content = apply_style_transfer(generated_content, style)
            
#             # Split into paragraphs and process
#             paragraphs = [p.strip() for p in styled_content.split('\n\n') if p.strip()]
            
#             # Add marker for paragraphs that should have capitalized first lines
#             paragraphs[0] = "§CAPS§" + paragraphs[0]
            
#             logger.debug(f"Successfully wrote section {section_path}")

#             return paragraphs
                
#         except Exception as api_error:
#             log_api_error('write_section.api_call', api_error,
#                          section_path=section_path,
#                          provider=provider)
#             raise Exception(f"API call failed: {str(api_error)}")
            
#     except Exception as e:
#         log_api_error('write_section', e, 
#                      section_path=section_path,
#                      topic=topic,
#                      style=style,
#                      provider=provider)
#         raise Exception(f"Failed to write section {section_path}: {str(e)}")

# Modify the write_full_article function signature and implementation
def write_full_article(
    topic: str,
    original_plan: str,
    structured_plan: ArticleStructure,
    style: str = "new_yorker",
    provider: ProviderType = "openai",
    include_headers: bool = True
) -> ArticleStructure:
    """Write the entire article or short story, generating each paragraph individually."""
    try:
        # Create a deep copy of the structured plan to preserve the original
        written_article = ArticleStructure(
            length=structured_plan.length,
            content=structured_plan.content.model_copy(deep=True)
        )

        logger.info(f"Starting full article writing process for {structured_plan.length} article, generating paragraphs individually")

        if isinstance(written_article.content, ShortArticleStructure):
            # Generate each paragraph individually
            for idx, paragraph in enumerate(written_article.content.paragraphs):
                paragraph_text = write_paragraph(
                    topic, original_plan, structured_plan, written_article, paragraph, style=style, provider=provider
                )
                written_article.content.paragraphs[idx].text = paragraph_text

        else:
            # Handle medium and long articles
            if isinstance(written_article.content, MediumArticleStructure):
                # Write introduction paragraphs
                for idx, paragraph in enumerate(written_article.content.intro_paragraphs):
                    paragraph_text = write_paragraph(
                        topic, original_plan, structured_plan, written_article,
                        paragraph, style=style, provider=provider
                    )
                    written_article.content.intro_paragraphs[idx].text = paragraph_text

                # Write main headings and their paragraphs
                for heading in written_article.content.main_headings:
                    for idx, paragraph in enumerate(heading.paragraphs):
                        paragraph_text = write_paragraph(
                            topic, original_plan, structured_plan, written_article,
                            paragraph, style=style, provider=provider
                        )
                        heading.paragraphs[idx].text = paragraph_text

                # Write conclusion paragraphs
                for idx, paragraph in enumerate(written_article.content.conclusion_paragraphs):
                    paragraph_text = write_paragraph(
                        topic, original_plan, structured_plan, written_article,
                        paragraph, style=style, provider=provider
                    )
                    written_article.content.conclusion_paragraphs[idx].text = paragraph_text

            elif isinstance(written_article.content, LongArticleStructure):
                # Write introduction paragraphs
                for idx, paragraph in enumerate(written_article.content.intro_paragraphs):
                    paragraph_text = write_paragraph(
                        topic, original_plan, structured_plan, written_article, paragraph, style=style, provider=provider
                    )
                    written_article.content.intro_paragraphs[idx].text = paragraph_text

                # Write main headings and their nested content
                for heading in written_article.content.main_headings:
                    # Write main heading paragraphs
                    for idx, paragraph in enumerate(heading.paragraphs):
                        paragraph_text = write_paragraph(
                            topic, original_plan, structured_plan, written_article,
                            paragraph, style=style, provider=provider
                        )
                        heading.paragraphs[idx].text = paragraph_text

                    # Write subheadings
                    for subheading in heading.sub_headings:
                        for idx, paragraph in enumerate(subheading.paragraphs):
                            paragraph_text = write_paragraph(
                                topic, original_plan, structured_plan, written_article,
                                paragraph, style=style, provider=provider
                            )
                            subheading.paragraphs[idx].text = paragraph_text

                        # Write sub-subheadings
                        for subsubheading in subheading.sub_headings:
                            for idx, paragraph in enumerate(subsubheading.paragraphs):
                                paragraph_text = write_paragraph(
                                    topic, original_plan, structured_plan, written_article,
                                    paragraph, style=style, provider=provider
                                )
                                subsubheading.paragraphs[idx].text = paragraph_text

                # Write conclusion paragraphs
                for idx, paragraph in enumerate(written_article.content.conclusion_paragraphs):
                    paragraph_text = write_paragraph(
                        topic, original_plan, structured_plan, written_article,
                        paragraph, style=style, provider=provider
                    )
                    written_article.content.conclusion_paragraphs[idx].text = paragraph_text

        logger.info(f"Successfully completed writing full article using {provider} with paragraph-level generation")
        return written_article

    except Exception as e:
        log_api_error('write_full_article', e,
                      topic=topic,
                      length=structured_plan.length,
                      provider=provider)
        raise Exception(f"Failed to write full article: {str(e)}")


def format_written_content(
    written_article: Union[
        ArticleStructure, ShortArticleStructure, MediumArticleStructure, LongArticleStructure
    ],
    include_headers: bool = True
) -> str:
    content = []

    # Check if written_article is an ArticleStructure
    if isinstance(written_article, ArticleStructure):
        # Extract the content attribute
        article_content = written_article.content
    else:
        # It's already a specific article structure
        article_content = written_article

    # Add title if headers are included
    if include_headers:
        title = article_content.title
        content.append(f"# {title}\n")

    # Handle different article structures
    if isinstance(article_content, ShortArticleStructure):
        for paragraph in article_content.paragraphs:
            if paragraph.text:
                content.append(paragraph.text)
    elif isinstance(article_content, MediumArticleStructure):
        # Introduction
        for paragraph in article_content.intro_paragraphs:
            if paragraph.text:
                content.append(paragraph.text)
        content.append("")

        # Main headings
        for heading in article_content.main_headings:
            if include_headers:
                content.append(f"## {heading.title}")
            for paragraph in heading.paragraphs:
                if paragraph.text:
                    content.append(paragraph.text)
            content.append("")

        # Conclusion
        for paragraph in article_content.conclusion_paragraphs:
            if paragraph.text:
                content.append(paragraph.text)
    elif isinstance(article_content, LongArticleStructure):
        # Introduction
        for paragraph in article_content.intro_paragraphs:
            if paragraph.text:
                content.append(paragraph.text)
        content.append("")

        # Main headings and nested content
        for heading in article_content.main_headings:
            if include_headers:
                content.append(f"## {heading.title}")
            for paragraph in heading.paragraphs:
                if paragraph.text:
                    content.append(paragraph.text)
            content.append("")

            for sub in heading.sub_headings:
                if include_headers:
                    content.append(f"### {sub.title}")
                for paragraph in sub.paragraphs:
                    if paragraph.text:
                        content.append(paragraph.text)
                content.append("")

                for subsub in sub.sub_headings:
                    if include_headers:
                        content.append(f"#### {subsub.title}")
                    for paragraph in subsub.paragraphs:
                        if paragraph.text:
                            content.append(paragraph.text)
                    content.append("")

        # Conclusion
        for paragraph in article_content.conclusion_paragraphs:
            if paragraph.text:
                content.append(paragraph.text)
    else:
        # Handle any other cases if necessary
        pass

    # Process the content to apply special formatting (if any)
    final_content = "\n".join(content).strip()
    return final_content

def write_paragraph(
    topic: str,
    original_plan: str,
    structured_plan: ArticleStructure,
    written_content: Union[ArticleStructure, ShortArticleStructure, MediumArticleStructure, LongArticleStructure],
    paragraph: Paragraph,
    style: str = "new_yorker",
    provider: ProviderType = "openai"
) -> str:
    """Write a specific paragraph of the article or short story."""
    try:
        # Format the content that's been written so far
        formatted_content = format_written_content(written_content)

        # Get the paragraph description and must_include information
        paragraph_description = paragraph.paragraph_description
        must_include = paragraph.must_include

        logger.info(f"Writing paragraph: {paragraph_description}")

        # Get the selected style details
        style_details = AVAILABLE_STYLES.get(style.lower(), AVAILABLE_STYLES["new_yorker"])

        prompt = f"""
<style guide>

You are an expert author writing in the style of {style_details.name}.

Style Description: {style_details.description}

Example of the style:
{style_details.example}

You may not use any of the following words or phrases: {', '.join(FORBIDDEN_WORDS)}

Write in clear, distinct paragraphs.

Do not include any headers, but you may use markdown to apply bolding, italics, and underlining.

Unless it's asbolutley critical to the story, all human characters should be either male or female.

</style guide>

<instructions>

Write the next section of the article or short story, maintaining consistency with previously written content and the overall plan.

Original Topic:

{topic}

Original Plan:

{original_plan}

Structured Plan for the Article or Short Story:

{structured_plan.model_dump_json()}

Content Written So Far:

{formatted_content}

Please write the next section that:

- Follows this description: {paragraph_description}
- Must include: {must_include}

Make sure the next section flows naturally from the previous content.

Make sure to bias each scene to contain a lot of character actions or dialogue. We don't want the story to drag. 

Do not return any text other than the next section of the article or short story.

</instructions>
"""

        if provider == "anthropic":
            completion = anthropic_client.messages.create(
                model="claude-3-5-sonnet-latest",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=8000
            )
            generated_content = completion.content[0].text.strip()
        else:
            completion = openai.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=[{"role": "user", "content": prompt}],
            )
            generated_content = completion.choices[0].message.content.strip()

        # Log the output
        db.save_llm_call_log(
            prompt,
            generated_content
        )

        # Apply style transfer (which handles forbidden words)
        styled_content = apply_style_transfer(
            content=generated_content,
            paragraph_description=paragraph_description,
            must_include=must_include,
            style_name=style,
            provider=provider
        )

        logger.debug(f"Successfully wrote paragraph")

        return styled_content

    except Exception as e:
        log_api_error('write_paragraph', e,
                      paragraph_description=paragraph.paragraph_description,
                      topic=topic,
                      style=style,
                      provider=provider)
        raise Exception(f"Failed to write paragraph: {str(e)}")
