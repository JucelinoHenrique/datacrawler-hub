from fastapi import APIRouter

from app.api.articles import router as articles_router
from app.api.scrape import router as scrape_router

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


router.include_router(articles_router)
router.include_router(scrape_router)
