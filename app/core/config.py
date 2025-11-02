import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "DataCrawler Hub")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    SCRAPE_INTERVAL_SECONDS: int = int(
        os.getenv("SCRAPE_INTERVAL_SECONDS", "1800")
    )  # 30 min
    SCRAPE_SOURCES: str = os.getenv("SCRAPE_SOURCES", "stub")


settings = Settings()
