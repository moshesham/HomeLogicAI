from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def scraper_client():
    # Import after conftest sets env vars so FileCache uses the temp dir.
    from main import app  # noqa: PLC0415

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(scraper_client: AsyncClient) -> None:
    resp = await scraper_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "scraper"


def test_domain_matches() -> None:
    from security import domain_matches

    assert domain_matches("https://www.homedepot.com/p/123", "homedepot.com")
    assert domain_matches("https://homedepot.com/p/123", "homedepot.com")
    assert not domain_matches("https://nothomedepot.com/p/123", "homedepot.com")


def test_validate_outbound_url_rejects_localhost() -> None:
    from security import validate_outbound_url

    with pytest.raises(ValueError, match="Localhost"):
        validate_outbound_url("http://localhost/foo")

    with pytest.raises(ValueError, match="Localhost"):
        validate_outbound_url("http://127.0.0.1/foo")


def test_validate_outbound_url_rejects_non_http() -> None:
    from security import validate_outbound_url

    with pytest.raises(ValueError, match="HTTP/HTTPS"):
        validate_outbound_url("ftp://example.com/file")


def test_file_cache_set_get_invalidate(tmp_path) -> None:
    from cache.file_cache import FileCache

    cache = FileCache(ttl_seconds=3600, cache_dir=tmp_path)
    url = "https://example.com/product/123"
    data = {"name": "Widget", "price": 9.99}

    assert cache.get(url) is None

    cache.set(url, data)
    result = cache.get(url)
    assert result == data

    cache.invalidate(url)
    assert cache.get(url) is None


def test_file_cache_ttl_expired(tmp_path) -> None:
    from cache.file_cache import FileCache
    import json
    from datetime import datetime, timedelta, timezone

    cache = FileCache(ttl_seconds=60, cache_dir=tmp_path)
    url = "https://example.com/old-product"
    data = {"name": "OldWidget"}

    cache.set(url, data)

    # Backdating the scraped_at to force expiry
    cache_file = cache._path(url)
    payload = json.loads(cache_file.read_text())
    payload["scraped_at"] = (
        datetime.now(timezone.utc) - timedelta(seconds=120)
    ).isoformat()
    cache_file.write_text(json.dumps(payload))

    assert cache.get(url) is None


def test_engine_detection() -> None:
    from engines.home_depot import HomeDepotScraper
    from engines.wayfair import WayfairScraper
    from engines.lowes import LowesScraper
    from engines.ikea import IkeaScraper
    from engines.amazon import AmazonScraper
    from engines.generic import GenericScraper

    assert HomeDepotScraper().detect("https://www.homedepot.com/p/item/123")
    assert not HomeDepotScraper().detect("https://www.wayfair.com/p/item")
    assert WayfairScraper().detect("https://www.wayfair.com/product/123")
    assert LowesScraper().detect("https://www.lowes.com/pd/item/123")
    assert IkeaScraper().detect("https://www.ikea.com/us/en/p/item/")
    assert AmazonScraper().detect("https://www.amazon.com/dp/B001")
    # Generic should always detect
    assert GenericScraper().detect("https://example.com/product")
