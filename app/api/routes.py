from fastapi import APIRouter

from app.api.articles import router as articles_router

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


router.include_router(articles_router)
