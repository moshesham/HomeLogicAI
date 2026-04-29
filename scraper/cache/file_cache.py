from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class FileCache:
    def __init__(self, ttl_seconds: int = 86400, cache_dir: Path | None = None) -> None:
        self.ttl_seconds = ttl_seconds
        self.cache_dir = cache_dir or Path("/app/data/scrape_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def _path(self, url: str) -> Path:
        return self.cache_dir / f"{self._key(url)}.json"

    def get(self, url: str) -> dict[str, Any] | None:
        path = self._path(url)
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        scraped_at = datetime.fromisoformat(payload["scraped_at"])
        ttl = int(payload.get("ttl", self.ttl_seconds))
        if datetime.now(timezone.utc) - scraped_at > timedelta(seconds=ttl):
            return None
        return payload.get("data")

    def set(self, url: str, data: dict[str, Any]) -> None:
        path = self._path(url)
        payload = {
            "url": url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "ttl": self.ttl_seconds,
            "data": data,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def invalidate(self, url: str) -> None:
        path = self._path(url)
        if path.exists():
            path.unlink()
