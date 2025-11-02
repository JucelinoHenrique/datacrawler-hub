from fastapi import FastAPI

from APP.api.routes import router as api_router
from APP.core.config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.include_router(api_router)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.VERSION}
