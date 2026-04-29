from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

from scraper.cache.file_cache import FileCache
from scraper.engines import (
    AmazonScraper,
    GenericScraper,
    HomeDepotScraper,
    IkeaScraper,
    LowesScraper,
    WayfairScraper,
)
from scraper.engines.base import BaseScraper
from scraper.engines.common import normalize_spec_map

app = FastAPI(title="HomeLogicAI Scraper", version="0.1.0", description="Retail scraper service")


class ScrapeRequest(BaseModel):
    url: HttpUrl
    force_refresh: bool = False


_ENGINES: list[BaseScraper] = [
    HomeDepotScraper(),
    WayfairScraper(),
    LowesScraper(),
    IkeaScraper(),
    AmazonScraper(),
    GenericScraper(),
]
_cache = FileCache()


def _detect_engine(url: str) -> BaseScraper:
    for engine in _ENGINES:
        if engine.detect(url):
            return engine
    return GenericScraper()


def _detect_retailer(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    hostname = hostname.lower()
    if "homedepot.com" in hostname:
        return "home_depot"
    if "wayfair" in hostname:
        return "wayfair"
    if "lowes.com" in hostname:
        return "lowes"
    if "ikea" in hostname:
        return "ikea"
    if "amazon" in hostname:
        return "amazon"
    return "generic"


@app.post("/scrape")
async def scrape_product(payload: ScrapeRequest) -> dict:
    url = str(payload.url)

    if not payload.force_refresh:
        cached = _cache.get(url)
        if cached is not None:
            return {**cached, "cache_hit": True}

    engine = _detect_engine(url)
    retailer = _detect_retailer(url)

    try:
        raw = await engine.scrape(url)
        raw_specs = raw.get("raw_specs") or {}
        normalized = normalize_spec_map(raw_specs)

        result = {
            "name": raw.get("name") or url,
            "price": raw.get("price"),
            "currency": raw.get("currency") or "USD",
            "images": raw.get("images") or [],
            "raw_specs": raw_specs,
            "attributes": raw.get("attributes") or normalized,
            "retailer": raw.get("retailer") or retailer,
            "source_url": url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "is_partial": bool(raw.get("is_partial", False)),
        }
        if raw.get("category_hint"):
            result["category_hint"] = raw["category_hint"]

        _cache.set(url, result)
        return result
    except Exception as exc:  # noqa: BLE001
        partial_data = {
            "source_url": url,
            "retailer": retailer,
            "engine": engine.retailer_name,
            "name": url,
            "raw_specs": {},
            "images": [],
            "is_partial": True,
        }
        return {"error": str(exc), "partial_data": partial_data}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "scraper"}
