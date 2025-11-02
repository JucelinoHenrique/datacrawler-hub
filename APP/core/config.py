import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "DataCrawler Hub")
    VERSION: str = os.getenv("VERSION", "0.1.0")


settings = Settings()
