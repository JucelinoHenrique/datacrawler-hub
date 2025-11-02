from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Article
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticleIn


class ArticleService:
    def __init__(self, db: Session):
        self.repo = ArticleRepository(db)

    def list_recent(self, limit: int = 50) -> Iterable[Article]:
        limit = min(max(limit, 1), 200)  # guarda-chuva simples
        return self.repo.list_recent(limit=limit)

    def create(self, payload: ArticleIn) -> Article:
        # Regra: não permitir duplicidade por URL
        if self.repo.get_by_url(str(payload.url)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Article with this URL already exists",
            )
        return self.repo.create(
            title=payload.title,
            url=str(payload.url),
            source=payload.source,
            published_at=payload.published_at,
        )
