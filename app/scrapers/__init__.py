from __future__ import annotations

from typing import Dict, Type

from app.scrapers.base import BaseScraper
from app.scrapers.g1_scraper import G1TechScraper
from app.scrapers.hackernews_scraper import HackerNewsScraper
from app.scrapers.stub_scraper import StubScraper

SCRAPERS: Dict[str, Type[BaseScraper]] = {
    "stub": StubScraper,
    "hackernews": HackerNewsScraper,
    "g1": G1TechScraper,
    "g1-tecnologia": G1TechScraper, 
}


def get_scraper(name: str) -> BaseScraper:
    cls = SCRAPERS.get(name.lower())
    if not cls:
        raise KeyError(f"scraper '{name}' not found")
    return cls()
