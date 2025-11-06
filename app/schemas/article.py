from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ArticleIn(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    source: str = Field(min_length=1, max_length=100)
    published_at: Optional[datetime] = None
    image_url: Optional[HttpUrl] = None


class ArticleOut(ArticleIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
