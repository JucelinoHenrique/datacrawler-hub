from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.article import ArticleIn, ArticleOut
from app.services.article_service import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


def get_service(db: Session = Depends(get_db)) -> ArticleService:
    return ArticleService(db)


@router.get("", response_model=List[ArticleOut])
def list_articles(
    limit: int = Query(50, ge=1, le=200),
    service: ArticleService = Depends(get_service),
):
    return service.list_recent(limit=limit)


@router.post("", response_model=ArticleOut, status_code=201)
def create_article(
    payload: ArticleIn,
    service: ArticleService = Depends(get_service),
):
    return service.create(payload)
