from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List

from app.schemas.article import ArticleIn


class BaseScraper(ABC):
    source: str

    @abstractmethod
    async def fetch(self) -> Any: ...

    @abstractmethod
    async def parse(self, raw: Any) -> List[ArticleIn]: ...

    async def run(self) -> List[ArticleIn]:
        raw = await self.fetch()
        items = await self.parse(raw)
        return items
