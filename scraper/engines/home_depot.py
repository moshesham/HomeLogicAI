from __future__ import annotations

from scraper.engines.base import BaseScraper
from scraper.engines.common import clean_text, parse_price


class HomeDepotScraper(BaseScraper):
    def detect(self, url: str) -> bool:
        return "homedepot.com" in url.lower()

    @property
    def retailer_name(self) -> str:
        return "home_depot"

    async def scrape(self, url: str) -> dict:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector(
                '[data-testid="product-details"]', timeout=30000
            )

            name = clean_text(
                await page.eval_on_selector(
                    "h1.product-title", "el => el?.textContent || ''"
                )
            )
            price_text = clean_text(
                await page.eval_on_selector(
                    ".price-format__main-price", "el => el?.textContent || ''"
                )
            )

            spec_rows = await page.query_selector_all("table.specifications-table tr")
            raw_specs: dict[str, str] = {}
            for row in spec_rows:
                cells = await row.query_selector_all("th,td")
                if len(cells) >= 2:
                    key = clean_text(await cells[0].inner_text())
                    value = clean_text(await cells[1].inner_text())
                    if key and value:
                        raw_specs[key] = value

            image_nodes = await page.query_selector_all("img.mediagallery__image")
            images: list[str] = []
            for node in image_nodes:
                src = await node.get_attribute("src")
                if src and src not in images:
                    images.append(src)

            breadcrumbs = await page.query_selector_all(
                'nav[aria-label="Breadcrumb"] a'
            )
            breadcrumb_text = [clean_text(await b.inner_text()) for b in breadcrumbs]

            await browser.close()

        return {
            "name": name,
            "price": parse_price(price_text),
            "currency": "USD",
            "images": images,
            "raw_specs": raw_specs,
            "retailer": self.retailer_name,
            "category_hint": " > ".join([b for b in breadcrumb_text if b]),
        }
