from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class Paragraph(BaseModel):
    paragraph_description: str
    must_include: str
    text: Optional[str] = None

# Base content models
class SubSubHeading(BaseModel):
    title: str
    paragraphs: List[Paragraph]

class SubHeading(BaseModel):
    title: str
    paragraphs: List[Paragraph]
    sub_headings: List[SubSubHeading]

class MainHeading(BaseModel):
    title: str
    paragraphs: List[Paragraph]
    sub_headings: List[SubHeading]

# Short article structure (no headings)
class ShortArticleStructure(BaseModel):
    title: str
    paragraphs: List[Paragraph]

# Medium article structure (headings but no subheadings)
class MediumArticleStructure(BaseModel):
    title: str
    intro_paragraphs: List[str]
    main_headings: List[MainHeading]
    conclusion_paragraphs: List[str]

# Long article structure (full hierarchy)
class LongArticleStructure(BaseModel):
    title: str
    intro_paragraphs: List[str]
    main_headings: List[MainHeading]
    conclusion_paragraphs: List[str]

# Enum for article length
class ArticleLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

# Combined article structure that can represent any length
class ArticleStructure(BaseModel):
    length: ArticleLength
    content: ShortArticleStructure | MediumArticleStructure | LongArticleStructure

    class Config:
        extra = 'forbid'

class WrittenArticle(ArticleStructure):
    """Represents the fully written article with all content generated."""
    pass

class LLMCallLog(BaseModel):
    input_text: str
    output_text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
  