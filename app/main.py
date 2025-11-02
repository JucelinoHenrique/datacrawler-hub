from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.scheduler import ScrapeScheduler
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# instancia global

scheduler = ScrapeScheduler(
    interval_seconds=settings.SCRAPE_INTERVAL_SECONDS,
    sources=settings.SCRAPE_SOURCES.split(","),
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def on_shutdown():
    await scheduler.stop()


app.include_router(api_router)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.VERSION}
