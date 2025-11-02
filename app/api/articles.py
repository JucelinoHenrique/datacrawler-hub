from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Article
from app.db.session import get_db
from app.schemas.article import ArticleIn, ArticleOut

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=List[ArticleOut])
def list_articles(db: Session = Depends(get_db)):
    return db.query(Article).order_by(Article.created_at.desc()).limit(50).all()


@router.post("", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
def create_article(payload: ArticleIn, db: Session = Depends(get_db)):
    obj = Article(
        title=payload.title,
        url=str(payload.url),
        source=payload.source,
        published_at=payload.published_at,
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Article with this URL already exists"
        )
    return obj
