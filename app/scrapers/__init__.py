from __future__ import annotations

from typing import Dict, Type

from app.scrapers.base import BaseScraper
from app.scrapers.stub_scraper import StubScraper

SCRAPERS: Dict[str, Type[BaseScraper]] = {
    "stub": StubScraper,
}


def get_scraper(name: str) -> BaseScraper:
    cls = SCRAPERS.get(name.lower())
    if not cls:
        raise KeyError(f"scraper '{name}' not found")
    return cls()
