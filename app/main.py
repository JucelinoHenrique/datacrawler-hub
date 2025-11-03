import logging

from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.scheduler import ScrapeScheduler
from app.db.base import Base
from app.db.session import engine
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# instancia global

app.state.scheduler = ScrapeScheduler(
    interval_seconds=settings.SCRAPE_INTERVAL_SECONDS,
    sources=settings.SCRAPE_SOURCES.split(","),
)

origins = [
    "http://localhost:3000",  # front em dev (Next)
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logging.getLogger(__name__).info("app_starting")
    app.state.scheduler.start()


@app.on_event("shutdown")
async def on_shutdown():
    await app.state.scheduler.stop()


app.include_router(api_router)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.VERSION}
