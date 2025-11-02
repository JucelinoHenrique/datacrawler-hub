from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.scrapers import get_scraper
from app.services.article_service import ArticleService

router = APIRouter(prefix="/scrape", tags=["scrape"])


def get_service(db: Session = Depends(get_db)) -> ArticleService:
    return ArticleService(db)


@router.post("/{source}")
async def run_scraper(
    source: str, service: ArticleService = Depends(get_service)
) -> Dict[str, Any]:
    try:
        scraper = get_scraper(source)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    created = 0
    duplicates = 0
    errors = 0
    items = await scraper.run()

    for it in items:
        try:
            service.create(it)
            created += 1
        except HTTPException as ex:
            if ex.status_code == status.HTTP_409_CONFLICT:
                duplicates += 1
            else:
                errors += 1

    return {
        "source": source,
        "received": len(items),
        "created": created,
        "duplicates": duplicates,
        "errors": errors,
    }
