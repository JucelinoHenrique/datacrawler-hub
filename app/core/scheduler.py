from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

from app.db.session import SessionLocal
from app.scrapers import get_scraper
from app.services.article_service import ArticleService


@dataclass
class SchedulerState:
    last_run_start: datetime | None = None
    last_run_end: datetime | None = None
    last_duration_ms: int | None = None
    total_runs: int = 0
    last_result: Dict[str, Dict[str, int]] = field(default_factory=dict)  # por fonte


class ScrapeScheduler:
    def __init__(self, interval_seconds: int, sources: List[str]):
        self.interval = interval_seconds
        self.sources = [s.strip() for s in sources if s.strip()]
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self.state = SchedulerState()
        self._stop_evt = asyncio.Event()

    def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._loop(), name="scrape-scheduler")

    async def stop(self):
        self._stop_evt.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self):
        # primeiro delay pequeno para não bloquear startup
        await asyncio.sleep(1.0)
        while not self._stop_evt.is_set():
            started = time.perf_counter()
            self.state.last_run_start = datetime.now(timezone.utc)
            per_source: Dict[str, Dict[str, int]] = {}

            # trava para evitar sobreposição caso demore mais que o intervalo
            async with self._lock:
                for source in self.sources:
                    per_source[source] = await self._run_once(source)

            self.state.last_run_end = datetime.now(timezone.utc)
            self.state.last_duration_ms = int((time.perf_counter() - started) * 1000)
            self.state.total_runs += 1
            self.state.last_result = per_source

            # aguarda próximo ciclo
            try:
                await asyncio.wait_for(self._stop_evt.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                # timeout normal -> próximo ciclo
                pass

    async def _run_once(self, source: str) -> Dict[str, int]:
        """Executa um scraper e persiste artigos via Service."""
        created = 0
        duplicates = 0
        errors = 0

        try:
            scraper = get_scraper(source)
            items = await scraper.run()
        except Exception:
            # erro ao instanciar/rodar o scraper
            return {"received": 0, "created": 0, "duplicates": 0, "errors": 1}

        # nova sessão por execução (background não usa Depends)
        db = SessionLocal()
        service = ArticleService(db)
        try:
            for it in items:
                try:
                    service.create(it)
                    created += 1
                except Exception as ex:
                    # 409 vem como HTTPException no service — tratamos genericamente aqui
                    msg = getattr(ex, "detail", "")
                    if isinstance(msg, str) and "already exists" in msg:
                        duplicates += 1
                    else:
                        errors += 1
        finally:
            db.close()

        return {
            "received": len(items),
            "created": created,
            "duplicates": duplicates,
            "errors": errors,
        }
