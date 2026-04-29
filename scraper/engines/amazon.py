from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from scraper.engines.base import BaseScraper
from scraper.engines.common import clean_text, parse_price
from scraper.security import domain_matches, validate_outbound_url


class AmazonScraper(BaseScraper):
    def detect(self, url: str) -> bool:
        return domain_matches(url, "amazon.com")

    @property
    def retailer_name(self) -> str:
        return "amazon"

    async def _scrape_with_bs4(self, url: str) -> dict:
        validate_outbound_url(url)
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        page_text = soup.get_text(" ", strip=True).lower()
        if "captcha" in page_text or "enter the characters you see" in page_text:
            return {
                "name": (
                    clean_text(soup.select_one("#productTitle").get_text())
                    if soup.select_one("#productTitle")
                    else ""
                ),
                "price": None,
                "currency": "USD",
                "images": [],
                "raw_specs": {},
                "retailer": self.retailer_name,
                "is_partial": True,
                "captcha_detected": True,
            }

        name = (
            clean_text(soup.select_one("#productTitle").get_text())
            if soup.select_one("#productTitle")
            else ""
        )
        price_text = (
            clean_text(soup.select_one(".a-price-whole").get_text())
            if soup.select_one(".a-price-whole")
            else ""
        )

        raw_specs: dict[str, str] = {}
        table = soup.select_one("#productDetails_techSpec_section_1")
        if table:
            for row in table.select("tr"):
                key_el = row.select_one("th")
                val_el = row.select_one("td")
                if key_el and val_el:
                    key = clean_text(key_el.get_text())
                    val = clean_text(val_el.get_text())
                    if key and val:
                        raw_specs[key] = val

        bullets = soup.select("#feature-bullets li")
        for idx, bullet in enumerate(bullets, start=1):
            text = clean_text(bullet.get_text())
            if text:
                raw_specs[f"feature_{idx}"] = text

        images = []
        for image in soup.select('img[src*="images"]'):
            src = image.get("src")
            if src and src not in images:
                images.append(src)

        return {
            "name": name,
            "price": parse_price(price_text),
            "currency": "USD",
            "images": images,
            "raw_specs": raw_specs,
            "retailer": self.retailer_name,
            "is_partial": False,
        }

    async def _scrape_with_playwright(self, url: str) -> dict:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            if await page.query_selector('input[name="captcha"]'):
                partial = {
                    "name": clean_text(await page.title()),
                    "price": None,
                    "currency": "USD",
                    "images": [],
                    "raw_specs": {},
                    "retailer": self.retailer_name,
                    "is_partial": True,
                    "captcha_detected": True,
                }
                await browser.close()
                return partial

            await page.wait_for_selector("#productTitle", timeout=30000)
            name = clean_text(
                await page.eval_on_selector(
                    "#productTitle", "el => el?.textContent || ''"
                )
            )
            price_text = clean_text(
                await page.eval_on_selector(
                    ".a-price-whole", "el => el?.textContent || ''"
                )
            )

            raw_specs: dict[str, str] = {}
            rows = await page.query_selector_all(
                "#productDetails_techSpec_section_1 tr"
            )
            for row in rows:
                cells = await row.query_selector_all("th,td")
                if len(cells) >= 2:
                    key = clean_text(await cells[0].inner_text())
                    value = clean_text(await cells[1].inner_text())
                    if key and value:
                        raw_specs[key] = value

            bullets = await page.query_selector_all("#feature-bullets li")
            for idx, bullet in enumerate(bullets, start=1):
                text = clean_text(await bullet.inner_text())
                if text:
                    raw_specs[f"feature_{idx}"] = text

            image_nodes = await page.query_selector_all("img")
            images = []
            for node in image_nodes:
                src = await node.get_attribute("src")
                if src and "images" in src and src not in images:
                    images.append(src)

            await browser.close()

        return {
            "name": name,
            "price": parse_price(price_text),
            "currency": "USD",
            "images": images,
            "raw_specs": raw_specs,
            "retailer": self.retailer_name,
            "is_partial": False,
        }

    async def scrape(self, url: str) -> dict:
        bs4_data = await self._scrape_with_bs4(url)
        if bs4_data.get("name") and not bs4_data.get("captcha_detected"):
            return bs4_data
        return await self._scrape_with_playwright(url)
