from __future__ import annotations

from datetime import datetime, timezone
from typing import List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.schemas.article import ArticleIn
from app.scrapers.base import BaseScraper

async def fetch_og_image(page_url: str) -> str | None:
    """Tenta buscar a imagem principal (og:image) da página de destino."""
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            resp = await client.get(page_url)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        og = soup.find("meta", property="og:image") or soup.find(
            "meta", attrs={"name": "twitter:image"}
        )
        if og and og.get("content"):
            return og["content"].strip() or None
    except Exception:
        
        return None

    return None


class HackerNewsScraper(BaseScraper):
    source = "hackernews"

    async def fetch(self) -> str:
        headers = {
            "User-Agent": "DataCrawlerHub/0.1 (+https://example.com; contact@example.com)"
        }
        timeout = httpx.Timeout(10.0, connect=5.0)
        async with httpx.AsyncClient(
            headers=headers, timeout=timeout, follow_redirects=True
        ) as client:
            r = await client.get("https://news.ycombinator.com/")
            r.raise_for_status()
            return r.text  # HTML bruto

    async def parse(self, raw_html: str) -> List[ArticleIn]:
        soup = BeautifulSoup(raw_html, "html.parser")
        now = datetime.now(timezone.utc)
        results: List[ArticleIn] = []

        BASE = "https://news.ycombinator.com/"

        # Cada notícia principal está numa linha ".athing"; o link está em ".titleline a"
        for row in soup.select(".athing"):
            a = row.select_one(".titleline a")
            if not a:
                continue
            title = (a.text or "").strip()
            href = (a.get("href") or "").strip()
            if not title or not href:
                continue

            url = urljoin(BASE, href)
            image_url = await fetch_og_image(url)
            results.append(
                ArticleIn(
                    title=title,
                    url=url,
                    source=self.source,
                    published_at=now, 
                    image_url=image_url
                )
            )

        # Limite inicial para evitar flood acidental
        return results[:30]
