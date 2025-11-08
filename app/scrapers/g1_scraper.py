from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.schemas.article import ArticleIn
from app.scrapers.base import BaseScraper


G1_BASE = "https://g1.globo.com"
G1_TECNO = "https://g1.globo.com/tecnologia/"


async def fetch_og_image(page_url: str) -> Optional[str]:
    """Abre a página da matéria e tenta puxar og:image."""
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(page_url)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"].strip()

        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            return tw["content"].strip()

    except Exception:
        return None

    return None


class G1TechScraper(BaseScraper):
    source = "g1-tecnologia"

    async def fetch(self) -> str:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(G1_TECNO)
        resp.raise_for_status()
        return resp.text

    async def parse(self, raw_html: str) -> List[ArticleIn]:
        soup = BeautifulSoup(raw_html, "html.parser")
        now = datetime.now(timezone.utc)
        results: List[ArticleIn] = []

        items = soup.select("div.bastian-feed-item, div.feed-post")
        for item in items:
            # título
            title_el = item.select_one("a.feed-post-link") or item.select_one("a")
            if not title_el:
                continue

            title = (title_el.get_text(strip=True) or "").strip()
            href = (title_el.get("href") or "").strip()
            if not title or not href:
                continue

            url = href if href.startswith("http") else urljoin(G1_BASE, href)

            # 1) tenta imagem na listagem
            img_url: Optional[str] = None
            img_el = (
                item.select_one("img")  # imagem principal do card
                or item.select_one("picture img")
            )
            if img_el:
                # g1 às vezes joga a url em vários atributos
                for attr in ("src", "data-src", "data-lazy-src", "data-lazy", "data-original"):
                    val = img_el.get(attr)
                    if val:
                        img_url = val
                        break
                # se veio //g1... completa
                if img_url and img_url.startswith("//"):
                    img_url = "https:" + img_url

            # 2) se ainda não achou, abre a página e tenta og:image
            if not img_url:
                img_url = await fetch_og_image(url)

            results.append(
                ArticleIn(
                    title=title,
                    url=url,
                    source=self.source,
                    published_at=now,
                    image_url=img_url,
                )
            )

        return results[:30]