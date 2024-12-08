from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import logging
import asyncio

from app.services.llm_service import (
    generate_article_plan,
    structure_article_plan,
    write_full_article, 
    format_written_content,
    AVAILABLE_STYLES,
    critique_and_elaborate_article_plan
)
from app.schemas import ArticleLength
from app.constants.writing_styles import AVAILABLE_STYLES  # Import the styles
from app.services.audio_service import AudioService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/v1/write-article-stream")
async def write_article_stream(
    topic: str,
    style: str = "hemingway",
    length: str = "long",
    provider: str = "openai",
    includeHeaders: bool = True,
    includeAudio: bool = False  # new parameter
):
    # Convert length string to enum
    try:
        article_length = ArticleLength(length.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid length: {length}")

    async def event_generator():
        try:
            # Generate initial plan
            plan = generate_article_plan(topic, style, article_length, provider)
            plan_data = json.dumps({"type": "plan", "content": plan})
            yield f"data: {plan_data}\n\n"
            
            await asyncio.sleep(1)
            
            # Structure the plan
            structured_plan = structure_article_plan(plan, article_length, provider)
            outline_data = json.dumps({
                "type": "outline",
                "content": structured_plan.model_dump()
            })
            yield f"data: {outline_data}\n\n"
            
            await asyncio.sleep(1)
            
            # Critique and elaborate on the plan
            revised_plan = critique_and_elaborate_article_plan(topic, plan, structured_plan, style, article_length, provider)
            revised_plan_data = json.dumps({"type": "revised_plan", "content": revised_plan})
            yield f"data: {revised_plan_data}\n\n"
            
            await asyncio.sleep(1)
            
            # Re-structure the revised plan
            revised_structured_plan = structure_article_plan(revised_plan, article_length, provider)
            revised_outline_data = json.dumps({
                "type": "revised_outline",
                "content": revised_structured_plan.model_dump()
            })
            yield f"data: {revised_outline_data}\n\n"
            
            await asyncio.sleep(1)
            
            # Write the full article using the revised structured plan
            written_article, scene_script = write_full_article(
                topic, 
                revised_plan, 
                revised_structured_plan, 
                style=style, 
                provider=provider,
                include_headers=includeHeaders
            )
            
            # Format the article content
            formatted_content = format_written_content(
                written_article,
                include_headers=includeHeaders
            )

            # Prepare the complete response object
            complete_response = {
                "type": "complete_content",
                "content": {
                    "article": formatted_content,
                    "audio_path": None
                }
            }
            
            # Generate audio if requested
            if includeAudio:
                try:
                    audio_service = AudioService()
                    filename = audio_service.process_article(scene_script)
                    complete_response["content"]["audio_path"] = f"output/{filename}"
                except Exception as audio_error:
                    logger.error(f"Error generating audio: {str(audio_error)}")
                    complete_response["content"]["audio_error"] = str(audio_error)

            # Send the complete response
            response_data = json.dumps(complete_response)
            yield f"data: {response_data}\n\n"
            yield 'event: end\ndata: \n\n'
            
        except Exception as e:
            logger.error(f"Error in event_generator: {str(e)}", exc_info=True)
            error_data = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type='text/event-stream')

@router.get("/api/v1/styles")
async def get_styles():
    return {key: style.model_dump() for key, style in AVAILABLE_STYLES.items()}