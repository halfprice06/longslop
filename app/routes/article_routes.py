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

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/v1/write-article-stream")
async def write_article_stream(
    topic: str,
    style: str = "new_yorker",
    length: str = "long",
    provider: str = "openai",
    includeHeaders: bool = True
):
    # Convert length string to enum
    try:
        article_length = ArticleLength(length.lower())
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid length. Must be one of: {[l.value for l in ArticleLength]}"
        )
    
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
            written_article = write_full_article(
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
            article_data = json.dumps({"type": "article", "content": formatted_content})
            yield f"data: {article_data}\n\n"
            
            # Indicate the end of the stream
            yield 'event: end\ndata: \n\n'
            
        except Exception as e:
            logger.error(f"Error in event_generator: {str(e)}", exc_info=True)
            error_data = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type='text/event-stream')

@router.get("/api/v1/styles")
async def get_styles():
    return {key: style.model_dump() for key, style in AVAILABLE_STYLES.items()}