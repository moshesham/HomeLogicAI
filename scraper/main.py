from __future__ import annotations

from datetime import datetime, timezone

import httpx
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
from scraper.security import domain_matches, validate_outbound_url

try:
    from playwright.async_api import Error as PlaywrightError
except Exception:  # pragma: no cover
    PlaywrightError = RuntimeError

app = FastAPI(
    title="HomeLogicAI Scraper", version="0.1.0", description="Retail scraper service"
)


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
    if domain_matches(url, "homedepot.com"):
        return "home_depot"
    if domain_matches(url, "wayfair.com"):
        return "wayfair"
    if domain_matches(url, "lowes.com"):
        return "lowes"
    if domain_matches(url, "ikea.com"):
        return "ikea"
    if domain_matches(url, "amazon.com"):
        return "amazon"
    return "generic"


@app.post("/scrape")
async def scrape_product(payload: ScrapeRequest) -> dict:
    url = validate_outbound_url(str(payload.url))

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
    except (ValueError, httpx.HTTPError, PlaywrightError, TimeoutError, OSError):
        partial_data = {
            "source_url": url,
            "retailer": retailer,
            "engine": engine.retailer_name,
            "name": url,
            "raw_specs": {},
            "images": [],
            "is_partial": True,
        }
        return {
            "error": "Scraping failed for the requested URL",
            "partial_data": partial_data,
        }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "scraper"}
