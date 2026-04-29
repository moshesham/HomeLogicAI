from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup

from scraper.engines.base import BaseScraper
from scraper.engines.common import clean_text, parse_price


class GenericScraper(BaseScraper):
    def detect(self, url: str) -> bool:
        return True

    @property
    def retailer_name(self) -> str:
        return "generic"

    async def scrape(self, url: str) -> dict:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        title = clean_text(soup.title.get_text()) if soup.title else clean_text(url)

        price_text = ""
        for selector in [
            "[itemprop='price']",
            ".price",
            ".product-price",
            ".sale-price",
            "[data-price]",
        ]:
            node = soup.select_one(selector)
            if node:
                price_text = clean_text(node.get_text(" ", strip=True))
                break
        if not price_text:
            match = re.search(r"\$\s*[\d,]+(?:\.\d{1,2})?", soup.get_text(" ", strip=True))
            if match:
                price_text = match.group(0)

        raw_specs: dict[str, str] = {}
        for row in soup.select("table tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = clean_text(cells[0].get_text(" ", strip=True))
                value = clean_text(cells[1].get_text(" ", strip=True))
                if key and value:
                    raw_specs[key] = value

        if not raw_specs:
            dt_nodes = soup.select("dl dt")
            for dt in dt_nodes:
                dd = dt.find_next_sibling("dd")
                if dd:
                    key = clean_text(dt.get_text(" ", strip=True))
                    value = clean_text(dd.get_text(" ", strip=True))
                    if key and value:
                        raw_specs[key] = value

        images = []
        for node in soup.select('meta[property="og:image"], meta[name="og:image"]'):
            src = node.get("content")
            if src and src not in images:
                images.append(src)

        return {
            "name": title,
            "price": parse_price(price_text),
            "currency": "USD",
            "images": images,
            "raw_specs": raw_specs,
            "retailer": self.retailer_name,
            "is_partial": True,
        }
