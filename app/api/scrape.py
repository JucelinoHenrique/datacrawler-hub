from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.article_repo import ArticleRepository
from app.scrapers import SCRAPERS, get_scraper
from app.services.article_service import ArticleService

router = APIRouter(prefix="/scrape", tags=["scrape"])


def get_service(db: Session = Depends(get_db)) -> ArticleService:
    return ArticleService(db)

@router.post("/all")
async def run_all_scrapers(service: ArticleService = Depends(get_service)):
    results: Dict[str, Any] = {}

    for name, scraper_cls in SCRAPERS.items():
        scraper = scraper_cls()
        items = await scraper.run()

        created = 0
        duplicates = 0
        errors = 0

        for it in items:
            try:
                service.create(it)
                created += 1
            except HTTPException as ex:
                if ex.status_code == status.HTTP_409_CONFLICT:
                    duplicates += 1
                else:
                    errors += 1

        results[name] = {
            "received": len(items),
            "created": created,
            "duplicates": duplicates,
            "errors": errors,
        }

    return {"status": "ok", "scrapers": results}


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


