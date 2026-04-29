from __future__ import annotations

from scraper.engines.base import BaseScraper
from scraper.engines.common import clean_text, parse_price


class IkeaScraper(BaseScraper):
    def detect(self, url: str) -> bool:
        return "ikea." in url.lower()

    @property
    def retailer_name(self) -> str:
        return "ikea"

    async def scrape(self, url: str) -> dict:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector(".product-header__title", timeout=30000)

            name = clean_text(
                await page.eval_on_selector(".product-header__title", "el => el?.textContent || ''")
            )
            price_text = clean_text(
                await page.eval_on_selector(".pip-price__integer", "el => el?.textContent || ''")
            )

            feature_nodes = await page.query_selector_all(".product-details__feature-list li")
            raw_specs: dict[str, str] = {}
            for index, node in enumerate(feature_nodes, start=1):
                value = clean_text(await node.inner_text())
                if value:
                    raw_specs[f"feature_{index}"] = value

            images = []
            image_nodes = await page.query_selector_all("img")
            for node in image_nodes:
                src = await node.get_attribute("src")
                if src and ("ikea" in src or "images" in src) and src not in images:
                    images.append(src)

            await browser.close()

        return {
            "name": name,
            "price": parse_price(price_text),
            "currency": "USD",
            "images": images,
            "raw_specs": raw_specs,
            "retailer": self.retailer_name,
            "variant_selection": "base",
        }
