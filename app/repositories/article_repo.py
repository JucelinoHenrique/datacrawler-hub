from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Article


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

        # CREATE

    def create(
        self, *, title: str, url: str, source: str, published_at=None
    ) -> Article:
        obj = Article(
            title=title,
            url=url,
            source=source,
            published_at=published_at,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_recent(self, limit: int = 50) -> Iterable[Article]:
        stmt = select(Article).order_by(Article.created_at.desc()).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def get_by_url(self, url: str) -> Optional[Article]:
        stmt = select(Article).where(Article.url == url)
        return self.db.execute(stmt).scalar_one_or_none()
