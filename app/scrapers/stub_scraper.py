from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.schemas.article import ArticleIn
from app.scrapers.base import BaseScraper


class StubScraper(BaseScraper):
    source = "stub"

    async def fetch(self):
        return [
            {"title": "Notícia A", "url": "https://example.com/a"},
            {"title": "Notícia B", "url": "https://example.com/b"},
            {"title": "Notícia C", "url": "https://example.com/c"},
        ]

    async def parse(self, raw) -> List[ArticleIn]:
        now = datetime.now(timezone.utc)
        items: List[ArticleIn] = []
        for item in raw:
            items.append(
                ArticleIn(
                    title=item["title"],
                    url=item["url"],
                    source=self.source,
                    published_at=now,
                )
            )
            return items
