from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Article
from app.db.session import get_db

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
def get_metrics(db: Session = Depends(get_db)):
    total_articles = db.query(func.count(Article.id)).scalar() or 0
    scheduler = Request.app.state.scheduler
    s = scheduler.state
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "articles": {
            "total": total_articles,
        },
        "scheduler": {
            "interval_seconds": scheduler.interval,
            "sources": scheduler.sources,
            "total_runs": s.total_runs,
            "last_run_start": s.last_run_start,
            "last_run_end": s.last_run_end,
            "last_duration_ms": s.last_duration_ms,
            "last_result": s.last_result,
        },
    }
