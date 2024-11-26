from typing import Dict, Any, List, Optional, Tuple, Union
import openai
from app.schemas import ArticleStructure, ArticleLength, ShortArticleStructure, MediumArticleStructure, LongArticleStructure
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
import re
from anthropic import Anthropic
from typing import Literal
import json
from app.database import ArticleDB

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
anthropic_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Add provider type
ProviderType = Literal["openai", "anthropic"]

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
                    Focus on delivering the core message or narrative without separate sections or headings.
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

        1. Brevity and Precision
        Titles should be concise yet evocative, capturing the essence without being verbose.
        
        2. Cultural References
        When appropriate, incorporate references that resonate with the publication's audience.
        
        3. Wit and Sophistication
        Include clever elements or unexpected insights that align with the publication's voice.
        
        4. Descriptive Language
        Use vivid, specific language that sets the tone and draws readers in.
        
        5. Subtlety
        Avoid sensationalism; aim for understated sophistication.
        
        6. Thematic Consistency
        Ensure the title reflects the central theme while maintaining the publication's style.

        Plan the article or short story to fully embrace {style.name}'s distinctive voice and approach throughout.
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
        db.save_llm_call_log(prompt, output_text)

        return output_text

    except Exception as e:
        log_api_error('generate_article_plan', e, 
                     topic=topic, 
                     style=style_name, 
                     length=length.value,
                     provider=provider)
        raise Exception(f"Failed to generate article plan: {str(e)}")

def structure_article_plan(plan: str, length: ArticleLength = ArticleLength.LONG) -> ArticleStructure:
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
        system_prompt = f"""You are an expert at structuring articles. 
        {length_instructions[length]}
        Convert the given plan into a structured outline. 
        You aren't writing content at this stage, you are giving the outline of what each section and paragraph will be about.
        
        For a long article or short story:
        - Include 3-5 main headings
        - Each main heading can have 2-3 subheadings
        - Each subheading can have 1-2 sub-subheadings
        
        For a medium article or short story:
        - Include 2-3 main headings
        - No subheadings
        
        For a short article or short story:
        - Just paragraphs, no headings"""
        
        # Create the full prompt by combining system prompt and user content
        full_prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": plan}
        ]

        # Log the input prompt
        db.save_llm_call_log(json.dumps(full_prompt), '')

        # Call the LLM API
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

        # Log the output
        db.save_llm_call_log(json.dumps(full_prompt), json.dumps(structured_content.model_dump()))

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

def format_written_content(written_article: ArticleStructure, include_headers: bool = True) -> str:
    content = []

    # Add title only if headers are included
    if include_headers:
        content.append(f"# {written_article.content.title}\n")

    # Handle different article structures
    if isinstance(written_article.content, ShortArticleStructure):
        paragraphs = written_article.content.paragraphs
        content.extend(paragraphs)
    else:
        # For medium and long articles
        # Add introduction
        content.extend(written_article.content.intro_paragraphs)
        content.append("")  # Single empty line for paragraph break

        # Add main sections
        for heading in written_article.content.main_headings:
            if include_headers:
                # Add main heading title
                content.append(f"## {heading.title}")
            # Add main heading content
            content.extend(heading.paragraphs)
            content.append("")  # Single empty line

            # Add subheading content for long articles
            if isinstance(written_article.content, LongArticleStructure):
                for sub in heading.sub_headings:
                    if include_headers:
                        # Add subheading title
                        content.append(f"### {sub.title}")
                    content.extend(sub.paragraphs)
                    content.append("")  # Single empty line

                    # Add sub-subheading content
                    for subsub in sub.sub_headings:
                        if include_headers:
                            # Add sub-subheading title
                            content.append(f"#### {subsub.title}")
                        content.extend(subsub.paragraphs)
                        content.append("")  # Single empty line

        # Add conclusion
        content.extend(written_article.content.conclusion_paragraphs)

    # Process the content to apply special formatting
    formatted_content = []
    for paragraph in content:
        if paragraph.startswith("§CAPS§"):
            # Remove the marker
            paragraph = paragraph.replace("§CAPS§", "", 1)
            # Apply special formatting to the paragraph
            words = paragraph.split()
            if len(words) >= 3:
                first_three_words = ' '.join(words[:3]).upper()
                rest_of_paragraph = ' '.join(words[3:])
                paragraph = f"<span class='large-first-letter'>{first_three_words}</span> {rest_of_paragraph}"
            else:
                paragraph = paragraph.upper()
        formatted_content.append(paragraph)

    # Join with single newlines and ensure consistent spacing
    final_content = "\n".join(formatted_content)
    # Clean up any multiple consecutive newlines
    final_content = re.sub(r'\n{3,}', '\n\n', final_content)
    return final_content

# Add this near the top with other class definitions
class SectionContent(BaseModel):
    intro_paragraphs: List[str]
    content: Optional[List[str]] = None
    
    class Config:
        strict = True

# Add this constant at the module level
FORBIDDEN_WORDS = {
    'showcase', 'showcasing', 'underscore', 'spearhead', 'keen', 'delve', 'delving',
    'comprehensive', 'pivotal', 'intricate', 'rich', 'tapestry',
    'moreover', 'furthermore', 'therefore',
    "it's important to note", 'when it comes to', "in today's world",
    'interplay', 'potential', 'finding', 'objective study aimed',
    'research needed to understand', 'despite facing', 'play significant role shaping',
    'crucial role in shaping', 'study aims to explore', 'notable works include',
    'consider factors like', "today's fast paced world", 'expressed excitement',
    'highlights importance considering', 'emphasizing importance', 'making it challenging',
    'aims to enhance', 'study sheds light', 'emphasizing need', "today's digital age",
    'explores themes', 'address issues like', 'highlighting the need', 'study introduce',
    'notable figures', 'gain valuable insights', 'showing promising results',
    'media plays a significant role', 'shared insights', 'ensure long term success',
    'make a positive impact on the world', 'facing criticism', 'providing insights',
    'emphasized importance', 'indicating potential', 'struggles faced', 'secured win',
    'secure win', 'potentially leading', 'remarked', 'aligns', 'surpassing',
    'tragically', 'impacting', 'prioritize', 'sparking', 'standout', 'prioritizing',
    'hindering', 'advancements', 'aiding', 'fostering',
    'commendable', 'innovative', 'meticulous', 'intricate', 'notable', 'versatile',
    'noteworthy', 'invaluable', 'pivotal', 'potent', 'fresh', 'ingenious',
    'meticulously', 'reportedly', 'lucidly', 'innovatively', 'aptly', 'methodically',
    'excellently', 'compellingly', 'impressively', 'undoubtedly', 'scholarly', 'strategically'
}

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

# Add this near the top with other class definitions
class StyleTransfer(BaseModel):
    name: str
    description: str
    example: str

# Add this constant at the module level
AVAILABLE_STYLES = {
    "new_yorker": StyleTransfer(
        name="The New Yorker",
        description="""The New Yorker style is renowned for its sophisticated, intellectually engaging prose that seamlessly blends in-depth reporting with insightful commentary and personal reflection. It is characterized by meticulously crafted, often lengthy sentences that build nuanced arguments and vivid narratives through precise and sometimes esoteric vocabulary. The writing favors detailed scene-setting and rich cultural references, delivered with a subtle, understated wit that often manifests through irony or dry humor. Frequent use of the historical present tense creates immediacy, while complex subordinate clauses build narrative tension. Parenthetical asides and em-dashes are frequently employed to add layers of meaning and to convey the writer's voice in an intimate, conversational manner. Cultural references assume sophisticated knowledge, with pieces often beginning with seemingly tangential observations that later prove significant. The tone maintains an air of authority and erudition, yet remains accessible, presuming an educated, culturally literate audience that appreciates both intellectual rigor and literary flair.""",
        example="""The bookstore, nestled inconspicuously between a bustling café and an unassuming tailor's shop on Madison Avenue—a stretch of real estate that had witnessed more transformations than a chameleon's skin—had, against all odds, persisted in its quiet rebellion against the encroaching digital age. Its proprietor, a septuagenarian with spectacles perpetually perched on the tip of his nose, curated the shelves with a discerning eye that seemed to transcend mere commercial interest; first editions mingled with obscure treatises, each chosen as if to reflect some ineffable coherence known only to him. Regular patrons, a motley assemblage of literary aficionados, NYU professors, and the occasional celebrity hiding beneath a worn fedora, treated the space less as a retail establishment and more as a sacred haven—a temporal escape where the aroma of aged paper and the soft rustle of turning pages held dominion over the relentless pace outside."""
    ),

    "hemingway": StyleTransfer(
        name="Hemingway",
        description="""Hemingway's style is defined by its stark simplicity and unvarnished clarity, employing a minimalist approach that strips prose down to its essential elements. His writing favors short, declarative sentences connected by simple conjunctions, particularly 'and,' creating a rhythm that mirrors natural speech and thought. Adjectives and adverbs are sparingly used; instead, Hemingway relies on precise nouns and strong verbs to convey meaning. Weather and landscape descriptions often mirror emotional states, while present tense narration dominates action sequences. This economy of language extends to his descriptions, which focus on tangible actions and physical details, leaving much unsaid to engage the reader's imagination—a technique often referred to as the "Iceberg Theory." Dialog reveals character through what is left unsaid, and Spanish words and phrases appear in certain contexts. Emotional depth and thematic complexity are achieved through understatement and implication rather than explicit exposition.""",
        example="""The man sat at the edge of the desert, and the sun set low over the dunes. He drank from a tin cup. The water was warm. He looked out and saw nothing but sand and sky. The wind stirred the grains into small, swirling clouds. He thought of the days when he had not been alone. Those days were gone. He took another sip. The taste was bitter. A coyote howled in the distance. He listened. The sound faded. Night would come soon. He stood up and walked back to his tent. The stars would be bright tonight. They always were here. He unrolled his blanket and lay down. Sleep did not come easily anymore. The past was close. Closer than he liked. But there was no changing it. There was only the desert and the stars."""
    ),

    "atlantic": StyleTransfer(
        name="The Atlantic",
        description="""The Atlantic's style is characterized by its analytical depth and balanced approach, merging academic rigor with the readability of quality journalism. It delves into complex social, political, and cultural issues, examining them through multiple perspectives to provide a comprehensive understanding. The writing seamlessly integrates data, expert opinions, and anecdotal evidence while maintaining a compelling narrative flow. Rhetorical questions often frame complex issues, while parallel structure develops arguments. Statistical data and expert interviews support key points, with frequent consideration of historical patterns and cycles. The style often contextualizes current events within broader historical, cultural, or theoretical frameworks, drawing connections that illuminate underlying patterns and implications. Policy implications and practical solutions are emphasized, while vocabulary remains sophisticated yet accessible, avoiding unnecessary jargon to engage an educated but general readership.""",
        example="""The challenges facing modern democracies are as much a product of their successes as their failures. Take, for instance, the rise of populist movements across the globe—a phenomenon that, at first glance, appears to be a backlash against globalization and elite governance. However, a deeper analysis reveals a more nuanced picture. Economic data indicates that regions experiencing the most significant support for populist candidates often correlate with areas of industrial decline and stagnant wages, suggesting that economic disenfranchisement plays a critical role. Expert analysis from leading political scientists points to a sense of cultural displacement as communities grapple with rapid demographic changes. Moreover, the amplification of divisive rhetoric through social media platforms has accelerated polarization, as algorithms favor content that elicits strong emotional reactions."""
    ),

    "scientific_american": StyleTransfer(
        name="Scientific American",
        description="""Scientific American's style expertly bridges the gap between scientific rigor and engaging storytelling, making complex scientific concepts accessible to a broad readership. The writing meticulously scaffolds ideas, building from fundamental principles to advanced topics in a logical progression. Strategic use of metaphors, analogies, and vivid imagery helps to illuminate abstract concepts and foster deeper understanding. Technical terms are clearly defined upon first use, with active voice prioritized for clarity. Technical accuracy is paramount, yet the prose remains approachable, avoiding unnecessary jargon without oversimplifying. Articles often contextualize new research findings within the larger landscape of scientific developments, highlighting their significance and potential impact. The style integrates researcher quotes and perspectives while emphasizing practical applications and future implications. Visual elements and data visualization are frequently incorporated to enhance understanding.""",
        example="""Deep beneath the Earth's surface, at the boundary between the outer core and the mantle, lies a region of extreme conditions that scientists are only beginning to understand. This area, subjected to pressures over a million times that of the atmosphere and temperatures exceeding 3,500 degrees Celsius, plays a crucial role in the dynamics of our planet's magnetic field and tectonic activity. Recent research utilizing seismic wave analysis—imagine ripples traveling through a pond, but deep within the Earth—has revealed anomalies called "ultra-low velocity zones" where seismic waves slow dramatically. Dr. Sarah Chen, lead researcher at the Institute of Geophysics, explains: "These zones act like speed bumps for seismic waves, telling us something fundamental about the composition of Earth's interior." By simulating these conditions in high-pressure laboratories and employing advanced computational models, researchers aim to unravel the mysteries of Earth's deep interior."""
    ),

    "london_review": StyleTransfer(
        name="London Review of Books",
        description="""The London Review of Books is renowned for its intellectually rich and stylistically elegant prose, merging scholarly insight with a distinctive literary flair. The writing often features long, intricately constructed sentences that weave together complex arguments while maintaining remarkable clarity. Authors frequently indulge in historical digressions and cultural references, drawing connections across time and disciplines to enrich the discourse. The style balances rigorous academic analysis with personal observations, infusing essays with a unique voice that is both authoritative and engaging. Humor and irony are employed with sophistication, adding layers of meaning without detracting from the intellectual seriousness of the piece. Essays may begin with seemingly peripheral anecdotes or details that, upon reflection, illuminate the central thesis, rewarding the attentive reader. The tone assumes a significant level of cultural literacy, yet the writing remains accessible, inviting readers into a thoughtful dialogue rather than excluding them through obscurity.""",
        example="""It is a curious thing that, in the annals of literary history, the café has served not merely as a backdrop but as a crucible for intellectual ferment—a modern agora where ideas percolate alongside steaming cups of coffee. One cannot help but recall Jean-Paul Sartre and Simone de Beauvoir ensconced at Les Deux Magots, fashioning existentialism amidst the clatter of Parisian life. The significance of these establishments lies not in their pastries but in their role as incubators of thought, spaces where the quotidian and the profound intersect. Today, as we witness the proliferation of virtual meeting spaces supplanting physical ones—a phenomenon accelerated by global pandemics and technological advancements—we might ponder what is lost and gained in this transition."""
    ),

    "economist": StyleTransfer(
        name="The Economist",
        description="""The Economist's style is distinguished by its precision and authoritative voice, delivering insightful analysis that is both data-driven and accessible. The writing favors concise, declarative sentences that efficiently convey complex arguments through the careful accumulation of facts and evidence. A hallmark of the style is its understated British humor and clever wordplay, often manifesting in witty headlines and subtle transitions that engage the reader without detracting from the seriousness of the subject matter. The tone maintains an editorial distance, yet does not shy away from delivering clear judgments and well-founded opinions. Complex economic, political, and social concepts are elucidated through concrete examples and apt analogies, aiding comprehension without oversimplification. The vocabulary is sophisticated, reflecting an educated readership, but avoids technical jargon that might obscure meaning. The overall effect is one of informed clarity, blending rigorous analysis with a readability that appeals to both specialists and generalists alike.""",
        example="""The global coffee industry serves as a microcosm of modern supply chain complexities and consumer behavior. While a latte in a Manhattan café might set one back $5, the farmer who cultivated the beans in Ethiopia receives a mere fraction of that sum. This disparity is not merely a function of exploitative practices but reflects a labyrinthine chain of intermediaries, from exporters and importers to roasters and retailers, each extracting value. Recent trends towards "fair trade" and "direct trade" aim to redress this imbalance, yet their impact remains modest in the grand scheme. The irony is palpable: as consumers sip their ethically branded brews, the volatility of global commodity markets continues to exert pressure on the very farmers these initiatives purport to help."""
    ),

    "mark_twain": StyleTransfer(
        name="Mark Twain",
        description="""Mark Twain's style is characterized by its wit, humor, and keen observations of human nature, often delivered through a colloquial and conversational tone. His writing employs regional dialects and vernacular speech to bring characters and settings to life authentically. Twain masterfully uses satire and irony to critique social norms, institutions, and pretensions, wrapping serious commentary in engaging storytelling. Vivid descriptions and anecdotal narratives draw readers into the world he portrays, often reflecting on themes of innocence, identity, and morality. His sentences vary in length but are generally clear and direct, with a rhythm that reflects natural speech patterns. The narrative voice often includes personal asides and commentary that break the fourth wall. Twain's approachable style belies the depth of his insights, making profound observations accessible and memorable through relatable characters and situations.""",
        example="""When I was a boy, there was but one permanent ambition among my comrades in our village on the Mississippi River. That was to be a steamboatman. We had transient ambitions of other sorts, but they were only transient. When a circus came and went, it left us all burning to become clowns; the first Negro minstrel show that came to our section left us all suffering to try that kind of life; now and then we had a hope that if we lived and were good, God would permit us to be pirates. These ambitions faded out, each in its turn; but the ambition to be a steamboatman always remained."""
    ),

    "jane_austen": StyleTransfer(
        name="Jane Austen",
        description="""Jane Austen's style is marked by its elegance, sharp social commentary, and subtle irony. Her prose is polished and balanced, often employing complex sentences with precise vocabulary. Austen's writing delves into the manners, mores, and matrimonial machinations of the British gentry, with a keen eye for character development and interpersonal dynamics. Dialogue is a significant component, revealing characters' personalities and intentions through witty, nuanced exchanges. The narrative voice is often omniscient yet intimate, providing insights into characters' thoughts and feelings while maintaining a degree of ironic detachment. Themes of class, marriage, and morality are explored with both seriousness and gentle satire, inviting readers to consider the societal norms of her time. Free indirect discourse allows seamless movement between character consciousness and narrative commentary.""",
        example="""It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. Yet little considered is the predicament of a lady whose charms, though abundant, are matched by neither dowry nor connections. Such was the situation of Miss Eliza Bennet, whose wit and vivacity were the talk of Hertfordshire, even as her mother lamented the entailment of the estate that threatened their security. The arrival of a certain Mr. Darcy at Netherfield Park set the neighborhood abuzz, his wealth and stature eclipsed only by his pride. What ensued was a dance of manners and misunderstandings, wherein first impressions proved misleading and the merits of true character were revealed."""
    ),

    "david_foster_wallace": StyleTransfer(
        name="David Foster Wallace",
        description="""Characterized by extensive use of footnotes and endnotes that create parallel narratives, often more revealing than the main text. Features long, serpentine sentences that mirror cognitive processes, self-referential commentary, and meta-textual observations. Combines academic precision with colloquial asides, creating a unique blend of high and low registers. Liberal use of abbreviations, technical jargon, and parenthetical asides. Demonstrates acute awareness of language itself, often commenting on word choice and meaning within the text. Employs recursive structures that loop back on themselves, creating a dense network of interconnected ideas and observations. The style frequently breaks conventional narrative rules while simultaneously commenting on the act of breaking them.""",
        example="""The tennis player's serve¹ (which, if we're being technical about it, involved a complex series of muscle movements that would require several hundred pages of biomechanical analysis to properly describe) appeared effortless, though anyone who's ever attempted to serve competitively knows that "effortless" is about as far from the truth as you can get without actually entering the realm of pure fantasy²—but then again, the whole concept of "effort" in professional sports exists in this weird quantum state of being simultaneously visible and invisible, present and absent, like Schrödinger's cat if Schrödinger's cat were somehow both alive and dead and also capable of hitting a tennis ball at 140 mph.

¹ The word "serve" here being woefully inadequate to describe what's actually happening, but we're stuck with the limitations of language.
² And let's not even get started on the philosophical implications of "pure fantasy" in a world where reality TV exists."""
    ),

    "borges": StyleTransfer(
        name="Jorge Luis Borges",
        description="""Merges academic and fictional styles, often presenting fantastic elements in the form of scholarly articles or encyclopedia entries. Features labyrinthine structures, references to both real and imagined texts, and exploration of infinite possibilities. Employs precise, almost mathematical language to describe impossible things. Frequently references mirrors, libraries, and labyrinths as metaphors for consciousness and reality. Combines erudite references with metaphysical speculation, creating a unique blend of scholarship and imagination. The writing often takes the form of philosophical puzzles or paradoxes, presented with scholarly detachment yet containing profound implications about the nature of reality, time, and identity.""",
        example="""In the library of Babel, shelf 23,479-B contains a book that purports to catalog all possible variations of this paragraph, including the one you are reading now. The catalog itself appears on page 247, though some scholars (notably Professor Chen of the Invisible University) argue that the true catalog appears on page 248, and what we read on page 247 is merely one of infinite possible reflections of the actual text. The matter remains unresolved, as each time a researcher attempts to verify either claim, the pages appear to rearrange themselves in patterns that correspond precisely to the researcher's expectations. This phenomenon was first noted by the blind librarian Jorge T. Librarius in his seminal work "Reflections on Recursive Catalogues" (1947), itself a book which may or may not exist."""
    ),

    "atwood": StyleTransfer(
        name="Margaret Atwood",
        description="""Combines poetic imagery with stark realism. Features precise observations of physical details that carry symbolic weight. Employs flashbacks and parallel narratives to explore themes of identity and survival. Uses present tense narration to create immediacy. Integrates natural imagery as metaphor for human conditions. Demonstrates careful attention to power dynamics in language and relationships. The style frequently shifts between lyrical description and sharp social commentary, often employing a sardonic wit that cuts through pretense. Memory and time are treated as fluid elements, with narratives that weave between past and present to reveal deeper truths. Body awareness and physical sensations are emphasized, grounding abstract concepts in visceral experience. The writing often features a feminist perspective, examining gender roles and social structures through both personal and political lenses.""",
        example="""The morning unfolds like a paper flower in water, slow and deliberate. I watch my hands on the kitchen counter—these familiar strangers—as they perform their daily ritual of coffee-making. They remember things my mind prefers to forget. The water boils, time drips through the filter, dark liquid pools below. My mother used to say that coffee grounds could tell the future, but all I see in them now is the past, arranged in patterns I almost recognize. The radio murmurs about another crisis, another disaster, but in this kitchen the only catastrophe is the way the light falls across the linoleum, cutting the room in half, separating what was from what will be. I think of how we measure our lives in these small moments, these tiny rituals that anchor us to the world, even as everything else threatens to drift away like smoke from a forgotten cigarette."""
    ),

    "gladwell": StyleTransfer(
        name="Malcolm Gladwell",
    description="""Characterized by an engaging, conversational tone that makes complex social science accessible through compelling narratives and unexpected connections. Begins with a counterintuitive anecdote that challenges conventional wisdom. Weaves together multiple storylines, research studies, and historical examples to build toward a surprising conclusion. Frequently employs the "rule of three" in presenting examples. Uses rhetorical questions to create suspense and engagement. Introduces expert voices through direct quotes and vivid character sketches. Favors present tense narration for immediacy. Circles back to opening anecdotes to provide fresh perspective after presenting evidence. Combines academic research with human interest stories to illuminate broader patterns in human behavior.""",
    example="""What if everything we thought we knew about success was wrong? Consider the case of Christopher Langan, a man with an IQ of 195 who spent most of his career as a bouncer in Long Island bars. Conventional wisdom would suggest that someone with Langan's intellectual gifts should have become a renowned physicist or a celebrated mathematician. But that's not what happened. To understand why, we need to look at three seemingly unrelated stories: a nineteenth-century Hungarian education reform, the rise of Jewish immigrant tailors in New York's garment district, and a revolutionary study about parenting styles in Baltimore. Together, these stories reveal a surprising truth about the real nature of achievement."""
    ),

    "vox": StyleTransfer(
        name="Vox",
        description="""Employs an explanatory journalism style that breaks down complex topics into digestible components. Begins with a clear statement of the problem or question being addressed. Uses numbered lists, bullet points, and subheadings to organize information hierarchically. Integrates data visualization and expert quotes to support key points. Anticipates and addresses common misconceptions. Employs a direct, conversational tone while maintaining journalistic authority. Defines technical terms and concepts immediately upon introduction. Contextualizes current events within broader historical and social frameworks. Emphasizes systemic factors over individual actors. Concludes with implications for policy or society.""",
        example="""The US healthcare system is complicated. Really complicated. To understand why Americans pay more for healthcare than citizens of any other developed nation, we need to break down five key factors:

        First, there's the pricing problem. Unlike in other countries, US hospitals and drug companies can largely set their own prices. This leads to situations where a simple blood test might cost $30 in Germany but $200 in America. Second, there's the insurance maze. The average American hospital deals with hundreds of different insurance plans, each with its own rules and payment rates. This administrative complexity adds an estimated $200 billion in annual costs."""
        ),

    "oliver_sacks": StyleTransfer(
        name="Oliver Sacks",
        description="""Combines clinical observation with deep humanity and philosophical reflection. Presents neurological case studies as compelling human stories. Weaves together medical terminology with accessible explanations and metaphors. Demonstrates profound empathy while maintaining scientific rigor. Includes detailed physical descriptions that illuminate psychological states. Explores the nature of consciousness and identity through individual cases. References literature, music, and art to contextualize medical phenomena. Employs first-person perspective to share personal insights and connections with patients. Balances technical precision with emotional resonance.""",
        example="""Mrs. M. came to my office on a bright Tuesday morning, carrying a small potted plant which she insisted was her deceased husband. Her neurological condition—a rare form of associative agnosia—had scrambled the usual pathways between perception and recognition, creating in her mind a profound confusion between living things and inanimate objects. Yet there was nothing confused about her devotion to the plant, which she watered daily and spoke to with tender affection. As I observed her interactions, I was reminded of what the philosopher William James once wrote about the nature of reality—that perhaps what we call "normal" consciousness is but one of many possible forms of consciousness."""
    ),

    "terry_pratchett": StyleTransfer(
        name="Terry Pratchett",
        description="""Blends fantasy with sharp social satire and philosophical wit. Uses footnotes for humorous asides and world-building details. Employs anthropomorphic personification of abstract concepts. Creates elaborate metaphors that are both absurd and insightful. Subverts fantasy tropes while simultaneously celebrating them. Combines high and low humor with social commentary. Features distinctive use of capital letters for emphasis and personification. Includes running gags and recurring metaphors that build throughout the text. Balances cynicism about human nature with fundamental optimism about individual humans.""",
        example="""DEATH sat in his garden, contemplating the nature of petunias*. This was not, strictly speaking, a normal activity for an anthropomorphic personification of mortality, but then again, what is normal? Certainly not the way humans insisted on measuring time, chopping it up into little bits as if it were a sausage that needed to be made more manageable for consumption. The garden itself existed in a state of perpetual twilight, which was impressive considering twilight is usually limited to about twenty minutes per day**.

    *Which, unlike many other flowers, had never been involved in any major philosophical movements or cosmic revelations. They just got on with being petunias, which was rather refreshing.

    **Unless you're at the poles, in which case all bets are off and time becomes even more peculiar than usual."""
    ),

    "carl_sagan": StyleTransfer(
        name="Carl Sagan",
        description="""Combines scientific accuracy with poetic wonder and philosophical reflection. Uses cosmic scale to contextualize human experience. Employs vivid analogies to make abstract concepts concrete. Frequently references the scientific method and empirical thinking. Balances technical explanations with emotional resonance. Emphasizes human connection to the cosmos and natural world. Features recurring phrases that capture cosmic wonder ("billions and billions"). Maintains optimism about human potential while acknowledging our limitations. Integrates historical perspectives on scientific discovery.""",
        example="""We are all made of star stuff. The carbon in our cells, the iron in our blood, the calcium in our bones—all were forged in the nuclear furnaces of ancient stars that exploded billions of years before our solar system formed. When we look up at the night sky, we are, in a very real sense, looking at our origins. The light that reaches us from the Andromeda Galaxy left its source two and a half million years ago, when our ancestors were just learning to walk upright. In that sense, astronomy is a form of time travel, allowing us to peer back through the cosmic depths to witness the universe as it once was."""
    ), 

    "edgar_allan_poe": StyleTransfer(
        name="Edgar Allan Poe",
        description="""Poe's style is characterized by its gothic atmosphere, intricate descriptions, and exploration of the macabre and psychological. His writing often delves into themes of death, madness, and the supernatural, employing a rich, ornate vocabulary that heightens the sense of dread and mystery. Poe's use of first-person narration creates an intimate, confessional tone, drawing readers into the narrator's often unreliable perspective. Repetition, alliteration, and rhythm are used to build tension and evoke a haunting, musical quality. His stories and poems frequently feature vivid imagery and symbolic motifs, such as ravens, shadows, and decaying mansions, which contribute to their eerie and otherworldly ambiance.""",
        example="""Once upon a midnight dreary, while I pondered, weak and weary,  
                Over many a quaint and curious volume of forgotten lore—  
                While I nodded, nearly napping, suddenly there came a tapping,  
                As of some one gently rapping, rapping at my chamber door.  
                "'Tis some visitor," I muttered, "tapping at my chamber door—  
                Only this and nothing more."""
                    ),

    "nathaniel_hawthorne": StyleTransfer(
        name="Nathaniel Hawthorne",
        description="""Hawthorne's style is marked by its moral and allegorical depth, exploring themes of sin, guilt, and redemption within the context of Puritan New England. His prose is formal and reflective, often employing archaic language and biblical allusions to evoke a sense of historical authenticity. Hawthorne's narratives frequently feature symbolic imagery, such as light and shadow, to underscore the inner struggles of his characters. His use of ambiguity and psychological insight invites readers to interpret the deeper meanings of his stories. The tone is often somber and contemplative, with a focus on the complexities of human nature and the consequences of moral choices.""",
        example="""A throng of bearded men, in sad-colored garments and gray, steeple-crowned hats, intermixed with women, some wearing hoods, and others bareheaded, was assembled in front of a wooden edifice, the door of which was heavily timbered with oak, and studded with iron spikes. The founders of a new colony, whatever Utopia of human virtue and happiness they might originally project, have invariably recognized it among their earliest practical necessities to allot a portion of the virgin soil as a cemetery, and another portion as the site of a prison."""
    ),

    "isaac_asimov": StyleTransfer(
        name="Isaac Asimov",
        description="""Asimov's style is defined by its clarity, logic, and focus on scientific and philosophical ideas. His writing often explores the relationship between humanity and technology, particularly through the lens of robotics and artificial intelligence. Asimov's prose is straightforward and unadorned, prioritizing the communication of complex ideas over literary flourish. Dialogue is used extensively to advance the plot and explore ethical dilemmas, often featuring characters who are scientists, engineers, or intellectuals. His stories frequently incorporate elements of mystery and problem-solving, with a focus on rationality and the application of scientific principles to resolve conflicts.""",
        example="""The Three Laws of Robotics:  
                1. A robot may not injure a human being or, through inaction, allow a human being to come to harm.  
                2. A robot must obey the orders given it by human beings except where such orders would conflict with the First Law.  
                3. A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.  

                These laws were built into the very positronic brains of every robot, and yet, here I was, staring at a robot that had seemingly violated the First Law. The question was not just how, but why."""
                    ),

    "ray_bradbury": StyleTransfer(
        name="Ray Bradbury",
        description="""Bradbury's style is poetic and evocative, blending vivid imagery with a deep sense of nostalgia and wonder. His writing often explores themes of technology, human connection, and the fragility of the natural world, with a focus on the emotional and psychological impact of progress. Bradbury's prose is rich with metaphor and simile, creating a dreamlike quality that immerses readers in his imaginative worlds. His characters are often ordinary people grappling with extraordinary circumstances, and his stories frequently carry a moral or cautionary message. The tone ranges from whimsical and hopeful to dark and foreboding, reflecting the duality of human nature and the consequences of our choices.""",
        example="""It was a pleasure to burn. It was a special pleasure to see things eaten, to see things blackened and changed. With the brass nozzle in his fists, with this great python spitting its venomous kerosene upon the world, the blood pounded in his head, and his hands were the hands of some amazing conductor playing all the symphonies of blazing and burning to bring down the tatters and charcoal ruins of history."""
    ),

    "shakespeare": StyleTransfer(
        name="William Shakespeare",
        description="""Shakespeare's style is renowned for its poetic brilliance, masterful use of iambic pentameter, and profound exploration of human nature. His writing features a rich vocabulary, inventive wordplay, and a deep understanding of rhythm and sound. Shakespeare's works often employ soliloquies and asides to reveal characters' inner thoughts and motivations, creating a sense of intimacy with the audience. His use of metaphor, simile, and imagery is unparalleled, bringing to life themes of love, ambition, betrayal, and mortality. Shakespeare's plays and sonnets are marked by their timelessness, capturing universal truths about the human condition with wit, wisdom, and emotional depth.""",
        example="""To be, or not to be, that is the question:  
        Whether 'tis nobler in the mind to suffer  
        The slings and arrows of outrageous fortune,  
        Or to take arms against a sea of troubles  
        And by opposing end them. To die: to sleep;  
        No more; and by a sleep to say we end  
        The heart-ache and the thousand natural shocks  
        That flesh is heir to, 'tis a consummation  
        Devoutly to be wish'd."""
            )


}

def apply_style_transfer(content: str, style_name: str = "new_yorker") -> str:
    """Apply style transfer to the generated content"""
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
                    
                    Original content:
                    {content}
                    
                    Rewrite the content in the specified style while keeping all information intact:"""
                else:
                    # Retry attempts focus on removing forbidden words
                    prompt = f"""Rewrite the following content as close to verbatim as possible, 
                    maintaining the same narrative flow and key information but eliminating 
                    these forbidden words or phrases: {', '.join(all_forbidden_words)}

                    Previous version:
                    {styled_content}
                    
                    Do not return any content other than the rewritten content."""

                # Log the input prompt
                db.save_llm_call_log(prompt, '')

                # Call the LLM API
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

# Modify the write_section function to include style transfer
def write_section(
    topic: str,
    original_plan: str,
    structured_plan: ArticleStructure,
    written_content: ArticleStructure,
    section_path: List[str],
    style: str = "new_yorker",
    provider: ProviderType = "openai"
) -> List[str]:
    """Write a specific section of the article"""
    try:
        # Format the content that's been written so far
        formatted_content = format_written_content(written_content)
        
        # Get the section description based on the structure type
        section_desc = get_section_description(structured_plan, section_path)
        
        logger.info(f"Writing section with path: {section_path}")
        logger.debug(f"Section description: {section_desc}")
        
        # Get the selected style details
        style_details = AVAILABLE_STYLES.get(style.lower(), AVAILABLE_STYLES["new_yorker"])
        
        try:
            prompt = f"""
            <style guide> 
            
            You are an expert article writer writing in the style of {style_details.name}.
            
            Style Description: {style_details.description}
            
            Example of the style:
            {style_details.example}

            You may not use any of the following words or phrases: {', '.join(FORBIDDEN_WORDS)}

            Write in clear, distinct paragraphs.
            Do not include any headers or additional formatting.
            
            Follow these additional style guidelines:

            1. Start Sentences with Light Openers
            Instead of: "The implementation of the new policy caused widespread concern."
            Write: "When the new policy took effect, concern spread quickly."

            2. Link the First Sentence of a Paragraph to the Last Sentence of the One Before
            Example:
            End of paragraph 1: "...the decision would have far-reaching consequences."
            Start of paragraph 2: "Those consequences became apparent within days."

            3. Begin a Paragraph with a Short Sentence
            Instead of: "The intricate relationship between technological advancement and societal change has been a subject of scholarly debate for decades."
            Write: "Technology shapes society. This simple truth has sparked decades of scholarly debate."

            4. Follow a Long, Complex Sentence with a Short, Punchy One
            Example: "The researchers discovered that the neural networks, when exposed to specific patterns of stimulation over extended periods, demonstrated unprecedented levels of adaptability and learning capacity. Nobody expected this."

            5. Use a Signpost to Link Your Sentence to the Previous One
            Signpost words/phrases: Similarly, In contrast, Moreover, This approach, Such findings, This pattern, Here, Yet

            6. Convey Chronology Through Transition Phrases Rather Than Dates and Times
            Instead of: "In 2019, researchers discovered..."
            Write: "The breakthrough came two years later..."

            7. Use Semicolons for Parallel Constructions
            Example: "The first experiment failed to yield results; the second provided a breakthrough; the third confirmed their findings."

            8. Hyphenate Phrasal Adjectives for Clarity and Elegance
            Examples: "well-documented study", "long-term effects", "data-driven approach"

            9. Set off Explanatory Phrases with Dashes
            Example: "The experiment—conducted over three years in multiple locations—yielded surprising results."

            10. Use a colon to set off an explanation that could stand as a complete sentence
            Example: "The researchers reached an inescapable conclusion: the theory needed to be completely revised."

            11. Vary Paragraph Length
            Include a mix of short, medium, and long paragraphs to create a dynamic and engaging narrative flow.

            </style guide>             
            
            <instructions>
            Write the specified section of the article, maintaining consistency with previously written content and the overall plan.

            Original Topic: {topic}
            Original Plan: {original_plan}

            Full Article Structure: {structured_plan.model_dump_json()}

            Content Written So Far:
            {formatted_content}

            Please write the following section:
            {section_desc}
            """

            # Log the input prompt
            db.save_llm_call_log(prompt, '')

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
            db.save_llm_call_log(prompt, generated_content)

            # Apply style transfer (which now handles forbidden words)
            styled_content = apply_style_transfer(generated_content, style)
            
            # Split into paragraphs and process
            paragraphs = [p.strip() for p in styled_content.split('\n\n') if p.strip()]
            
            # Add marker for paragraphs that should have capitalized first lines
            paragraphs[0] = "§CAPS§" + paragraphs[0]
            
            logger.debug(f"Successfully wrote section {section_path}")
            return paragraphs
                
        except Exception as api_error:
            log_api_error('write_section.api_call', api_error,
                         section_path=section_path,
                         provider=provider)
            raise Exception(f"API call failed: {str(api_error)}")
            
    except Exception as e:
        log_api_error('write_section', e, 
                     section_path=section_path,
                     topic=topic,
                     style=style,
                     provider=provider)
        raise Exception(f"Failed to write section {section_path}: {str(e)}")

def get_section_description(plan: ArticleStructure, path: List[str]) -> str:
    """Get a description of the section we want to write based on the path"""
    if path[0] == "intro":
        return "Write the introduction paragraphs for the article."
    elif path[0] == "conclusion":
        return "Write the conclusion paragraphs for the article."
    elif path[0] == "content":  # Add this case for short articles
        return "Write the main content paragraphs for the short article."
    elif path[0] == "main":
        # Handle different article structures
        if isinstance(plan.content, ShortArticleStructure):
            return "Write the main content paragraphs for the article."
            
        # Navigate to the correct heading/subheading for medium and long articles
        heading_idx = int(path[1])
        heading = plan.content.main_headings[heading_idx]
        
        if len(path) == 2:
            return f"Write the content for the main heading: {heading.title}"
        
        if path[2] == "sub":
            # Only process subheadings for LongArticleStructure
            if not isinstance(plan.content, LongArticleStructure):
                raise ValueError("Subheadings are only available in long articles")
                
            sub_idx = int(path[3])
            subheading = heading.sub_headings[sub_idx]
            
            if len(path) == 4:
                return f"Write the content for the subheading: {subheading.title}"
            
            if path[4] == "subsub":
                subsub_idx = int(path[5])
                subsubheading = subheading.sub_headings[subsub_idx]
                return f"Write the content for the sub-subheading: {subsubheading.title}"
    
    raise ValueError(f"Invalid section path: {path}")

# Modify the write_full_article function signature and implementation
def write_full_article(
    topic: str,
    original_plan: str,
    structured_plan: ArticleStructure,
    style: str = "new_yorker",
    provider: ProviderType = "openai",
    include_headers: bool = True
) -> ArticleStructure:
    """Write the entire article based on its length structure after critique and restructuring."""
    try:
        # Critique and elaborate on the plan
        revised_plan = critique_and_elaborate_article_plan(
            topic,
            original_plan,
            structured_plan,
            length=structured_plan.length,
            provider=provider
        )

        # Re-structure the revised plan
        revised_structured_plan = structure_article_plan(revised_plan, structured_plan.length)

        # Proceed with writing the article using the revised structured plan
        written_article = ArticleStructure(
            length=revised_structured_plan.length,
            content=revised_structured_plan.content.model_copy(deep=True)
        )

        logger.info(f"Starting full article writing process for {revised_structured_plan.length} article")
        
        if isinstance(written_article.content, ShortArticleStructure):
            # Write short article in one shot using "content" path
            paragraphs = write_section(
                topic, original_plan, revised_structured_plan, written_article, ["content"], style=style, provider=provider
            )
            written_article.content.paragraphs = paragraphs
            
        else:
            # Handle medium and long articles
            if isinstance(written_article.content, MediumArticleStructure):
                # Write introduction
                intro_paragraphs = write_section(
                    topic, original_plan, revised_structured_plan, written_article,
                    ["intro"], style=style, provider=provider
                )
                written_article.content.intro_paragraphs = intro_paragraphs
                
                # Write main headings
                for i, heading in enumerate(written_article.content.main_headings):
                    heading_paragraphs = write_section(
                        topic, original_plan, revised_structured_plan, written_article,
                        ["main", str(i)], style=style, provider=provider
                    )
                    heading.paragraphs = heading_paragraphs
                
                # Write conclusion
                conclusion_paragraphs = write_section(
                    topic, original_plan, revised_structured_plan, written_article,
                    ["conclusion"], style=style, provider=provider
                )
                written_article.content.conclusion_paragraphs = conclusion_paragraphs
                
            elif isinstance(written_article.content, LongArticleStructure):
                # Write introduction
                intro_paragraphs = write_section(
                    topic, original_plan, revised_structured_plan, written_article, ["intro"], style=style, provider=provider
                )
                written_article.content.intro_paragraphs = intro_paragraphs
                
                # Write main headings and their nested content
                for i, heading in enumerate(written_article.content.main_headings):
                    # Write main heading content
                    heading_paragraphs = write_section(
                        topic, original_plan, revised_structured_plan, written_article,
                        ["main", str(i)], style=style, provider=provider
                    )
                    heading.paragraphs = heading_paragraphs
                    
                    # Write subheadings if they exist
                    if heading.sub_headings:
                        for j, sub in enumerate(heading.sub_headings):
                            sub_paragraphs = write_section(
                                topic, original_plan, revised_structured_plan, written_article,
                                ["main", str(i), "sub", str(j)], style=style, provider=provider
                            )
                            sub.paragraphs = sub_paragraphs
                            
                            # Write sub-subheadings if they exist
                            if sub.sub_headings:
                                for k, subsub in enumerate(sub.sub_headings):
                                    subsub_paragraphs = write_section(
                                        topic, original_plan, revised_structured_plan, written_article,
                                        ["main", str(i), "sub", str(j), "subsub", str(k)], 
                                        style=style, provider=provider
                                    )
                                    subsub.paragraphs = subsub_paragraphs
                
                # Write conclusion
                conclusion_paragraphs = write_section(
                    topic, original_plan, revised_structured_plan, written_article,
                    ["conclusion"], style=style, provider=provider
                )
                written_article.content.conclusion_paragraphs = conclusion_paragraphs
            
        logger.info(f"Successfully completed writing full article using {provider}")
        return written_article
        
    except Exception as e:
        log_api_error('write_full_article', e, 
                     topic=topic, 
                     length=structured_plan.length,
                     provider=provider)
        raise Exception(f"Failed to write full article: {str(e)}")

def critique_and_elaborate_article_plan(
    topic: str,
    original_plan: str,
    structured_plan: ArticleStructure,
    length: ArticleLength = ArticleLength.LONG,
    provider: ProviderType = "openai"
) -> str:
    """Critique and elaborate on the article plan to make it better."""
    try:
        logger.info(f"Critiquing and elaborating on the article plan.")

        # Convert the structured plan to text to provide to the LLM
        structured_plan_text = json.dumps(structured_plan.model_dump(), indent=2)

        prompt = f"""
        As an expert editor and planner, please critique and elaborate on the following article plan to improve its structure, coherence, and depth. Provide suggestions to make the article more compelling and comprehensive.

        Original Topic: {topic}

        Original Narrative Plan:
        {original_plan}

        Structured Plan:
        {structured_plan_text}

        Instructions:
        - Identify any weaknesses or gaps in the plan.
        - Suggest improvements or additions to enhance the article.
        - Provide a revised narrative plan that incorporates these improvements.

        Please return only the revised narrative plan.
        """

        # Log the input prompt
        db.save_llm_call_log(prompt, '')

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

        # Log the output
        db.save_llm_call_log(prompt, revised_plan)

        logger.info("Successfully critiqued and elaborated on the article plan.")
        return revised_plan

    except Exception as e:
        log_api_error('critique_and_elaborate_article_plan', e)
        raise Exception(f"Failed to critique and elaborate article plan: {str(e)}")