from typing import List
from pydantic import BaseModel
from enum import Enum

# Base content models
class SubSubHeading(BaseModel):
    title: str
    paragraphs: List[str]

class SubHeading(BaseModel):
    title: str
    paragraphs: List[str]
    sub_headings: List[SubSubHeading]

class MainHeading(BaseModel):
    title: str
    paragraphs: List[str]
    sub_headings: List[SubHeading]

# Short article structure (no headings)
class ShortArticleStructure(BaseModel):
    title: str
    paragraphs: List[str]

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
  