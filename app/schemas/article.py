from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    content: str = Field(..., min_length=10)
    category: str = Field(default="Geral", max_length=50)
    tags: Optional[str] = Field(default=None, max_length=200)


class ArticleCreate(ArticleBase):
    pass


class ArticleResponse(ArticleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
