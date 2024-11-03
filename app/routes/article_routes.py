from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse
import json
from app.services.llm_service import (
    generate_article_plan,
    structure_article_plan,
    write_full_article, 
    format_written_content,
    AVAILABLE_STYLES
)
import logging
import asyncio
from fastapi import BackgroundTasks
from app.database import ArticleDB
from typing import List, Dict, Any
from pydantic import BaseModel
from app.schemas import ArticleLength

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()
db = ArticleDB()

# Add the missing ArticleRequest schema
class ArticleRequest(BaseModel):
    topic: str
    style: str = "new_yorker"
    length: ArticleLength = ArticleLength.LONG

class ArticleResponse(BaseModel):
    article: str

def format_sse_data(data: dict) -> str:
    """Format data as SSE message"""
    return f"data: {json.dumps(data)}\n\n"

def format_sse_event(event: str, data: str) -> str:
    """Format SSE event with custom event type"""
    return f"event: {event}\ndata: {data}\n\n"

@router.get("/api/v1/styles")
async def get_available_styles():
    """Endpoint to get available writing styles"""
    return {
        style_id: {
            "name": style.name,
            "description": style.description,
            "example": style.example
        } for style_id, style in AVAILABLE_STYLES.items()
    }

# Add this function to convert string to enum
def get_article_length(length_str: str) -> ArticleLength:
    """Convert string length to ArticleLength enum"""
    try:
        return ArticleLength(length_str.lower())
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid length. Must be one of: {', '.join([l.value for l in ArticleLength])}"
        )

@router.get("/api/v1/write-article-stream")
async def write_article_stream(
    topic: str,
    background_tasks: BackgroundTasks,
    style: str = "new_yorker",
    length: str = "long",
    provider: str = "openai",
    includeHeaders: bool = True
):
    try:
        # Convert length string to enum
        article_length = ArticleLength(length.lower())
        
        async def generate():
            try:
                # Generate initial plan
                plan = generate_article_plan(topic, style, article_length, provider)
                yield format_sse_data({"type": "plan", "content": plan})
                
                # Structure the plan
                structured_plan = structure_article_plan(plan, article_length)
                yield format_sse_data({"type": "outline", "content": structured_plan.model_dump()})
                
                # Write the full article
                written_article = write_full_article(
                    topic, 
                    plan, 
                    structured_plan, 
                    style=style, 
                    provider=provider,
                    include_headers=includeHeaders
                )
                
                # Format the article content
                formatted_content = format_written_content(
                    written_article,
                    include_headers=includeHeaders
                )
                
                yield format_sse_data({"type": "article", "content": formatted_content})
                yield format_sse_data({"type": "end"})
                
            except Exception as e:
                logger.error(f"Error in generate(): {str(e)}")
                yield format_sse_data({"type": "error", "content": str(e)})
                
        return EventSourceResponse(generate())
        
    except Exception as e:
        logger.error(f"Error in write_article_stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/articles")
async def get_articles() -> List[Dict[str, Any]]:
    """Get list of all articles"""
    return [dict(article) for article in db.get_article_list()]

@router.get("/api/articles/{article_id}")
async def get_article(article_id: int) -> Dict[str, Any]:
    """Get a specific article by ID"""
    article = db.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("/api/generate")
async def generate_article(request: ArticleRequest):
    """Generate a complete article"""
    try:
        # Generate initial plan
        plan = generate_article_plan(request.topic, request.style)
        
        # Structure the plan
        structured_plan = structure_article_plan(plan)
        
        # Write the full article
        written_article = write_full_article(request.topic, plan, structured_plan, style=request.style)
        
        # Save to database
        article_id = db.save_article(request.topic, request.style, written_article)
        
        # Format the content
        formatted_content = format_written_content(written_article)
        
        return {
            "article_id": article_id,
            "content": formatted_content
        }
        
    except Exception as e:
        logger.error(f"Error generating article: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/article/generate", response_model=ArticleResponse)
async def generate_article_endpoint(request: ArticleRequest):
    try:
        # Generate the initial plan
        plan = generate_article_plan(request.topic, request.style)
        
        # Structure the plan with the specified length
        structured_plan = structure_article_plan(plan, request.length)
        
        # Write the full article
        written_article = write_full_article(
            request.topic,
            plan,
            structured_plan,
            request.style
        )
        
        # Format the content
        formatted_content = format_written_content(written_article)
        
        return ArticleResponse(article=formatted_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_article(
    topic: str,
    style: str = "new_yorker",
    length: str = "long",
    provider: str = "openai"  # Add provider parameter
):
    try:
        # Generate initial plan
        plan = generate_article_plan(topic, style, length, provider=provider)
        
        # Structure the plan (always use OpenAI for this step)
        structure = structure_article_plan(plan, ArticleLength(length.lower()))
        
        # Write the full article
        article = write_full_article(topic, plan, structure, style, provider=provider)
        
        # Format the content
        formatted_content = format_written_content(article)
        
        return {"content": formatted_content, "plan": plan}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_article")
async def generate_article(request: Request):
    # ... existing code ...
    data = await request.json()
    include_headers = data.get('includeHeaders', True)
    # ... existing code ...

    article = write_full_article(
        topic=data['topic'],
        original_plan=data['original_plan'],
        structured_plan=structured_plan,
        style=data.get('style', 'new_yorker'),
        provider=data.get('provider', 'openai'),
        include_headers=include_headers  # Pass the parameter to the function
    )
    # ... existing code ...