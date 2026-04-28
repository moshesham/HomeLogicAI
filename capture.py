#!/usr/bin/env python3
"""
capture.py — HomeLogic Product Capture Service
================================================
Scrapes a product URL and saves structured JSON data to the vault.

Usage:
    python capture.py --url URL --category CATEGORY [--name "Custom Name"] [--no-image]

Examples:
    python capture.py --url "https://www.example.com/ceiling-fan" --category fans
    python capture.py --url "https://www.homedepot.com/p/..." --category lighting --name "Kitchen Pendant"
"""

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit(
        "Missing dependencies. Run:  pip install -r requirements.txt"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

VAULT_ROOT = Path(__file__).parent / "vault"
CONFIG_FILE = Path(__file__).parent / "config.yaml"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

REQUEST_TIMEOUT = 15  # seconds

# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text[:80]  # cap length


def load_config() -> dict:
    """Load config.yaml if present, otherwise return defaults."""
    if CONFIG_FILE.exists():
        try:
            import yaml  # optional — only needed if PyYAML is installed

            with open(CONFIG_FILE) as fh:
                return yaml.safe_load(fh) or {}
        except Exception:
            pass
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# Extraction helpers — selector-agnostic approach
# ─────────────────────────────────────────────────────────────────────────────


def _text(soup, *selectors) -> str:
    """Try a list of CSS selectors and return the first non-empty text found."""
    for sel in selectors:
        tag = soup.select_one(sel)
        if tag:
            return tag.get_text(separator=" ", strip=True)
    return ""


def extract_title(soup: BeautifulSoup, url: str) -> str:
    """
    Extract product title using a priority chain of common patterns,
    then fall back to the page <title>.
    """
    candidates = [
        # Structured data (most reliable)
        '[itemprop="name"]',
        # Common e-commerce patterns
        "h1.product-title",
        "h1.product_title",
        "h1.pdp-title",
        "h1.item-title",
        "#productTitle",
        ".product-name h1",
        ".product__title",
        "h1",  # generic last resort
    ]
    title = _text(soup, *candidates)
    if not title:
        title = soup.title.string.strip() if soup.title else urlparse(url).path
    # Strip common e-commerce suffixes
    title = re.sub(r"\s*[|\-–—].*$", "", title).strip()
    return title or "Unknown Product"


def extract_price(soup: BeautifulSoup) -> str:
    """Extract the first price-like string found on the page."""
    # Try structured data first
    for sel in [
        '[itemprop="price"]',
        '[class*="price"]',
        '[id*="price"]',
        ".Price",
        ".a-price .a-offscreen",  # Amazon
        "[data-price]",
    ]:
        tag = soup.select_one(sel)
        if tag:
            # Try data attribute first
            val = tag.get("content") or tag.get("data-price") or tag.get_text(strip=True)
            if val:
                match = re.search(r"\$[\d,]+\.?\d*", val)
                if match:
                    return match.group()
                if re.search(r"\d", val):
                    return val[:30]

    # Fallback: scan entire text for a price pattern
    text = soup.get_text(" ")
    match = re.search(r"\$\s*[\d,]+\.?\d{0,2}", text)
    return match.group().replace(" ", "") if match else "N/A"


def extract_dimensions(soup: BeautifulSoup) -> str:
    """Extract dimension/measurement strings from the page."""
    text = soup.get_text(" ")

    # Common patterns: 12 in x 24 in, 12" x 24", 30.5 cm x 60 cm, etc.
    patterns = [
        (
            r"\d+(?:\.\d+)?\s*(?:in|inch|inches|\")\s*[xX×]\s*\d+(?:\.\d+)?\s*(?:in|inch|inches|\")"
            r"(?:\s*[xX×]\s*\d+(?:\.\d+)?\s*(?:in|inch|inches|\"))?"
        ),
        r"\d+(?:\.\d+)?\s*cm\s*[xX×]\s*\d+(?:\.\d+)?\s*cm",
        r"\d+(?:\.\d+)?\s*mm\s*[xX×]\s*\d+(?:\.\d+)?\s*mm",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group().strip()

    # Try spec table rows labeled with dimension keywords
    for row in soup.select("tr, li, .spec-row, .spec-item, [class*='spec']"):
        row_text = row.get_text(" ", strip=True).lower()
        if any(kw in row_text for kw in ["dimension", "size", "width", "depth", "height", "diameter"]):
            return row.get_text(separator=" ", strip=True)[:120]

    return "N/A"


def extract_material(soup: BeautifulSoup) -> str:
    """Extract material/finish information."""
    text = soup.get_text(" ")

    # Look for labeled spec rows
    for row in soup.select("tr, li, .spec-row, [class*='spec'], [class*='detail']"):
        row_text = row.get_text(" ", strip=True).lower()
        if any(kw in row_text for kw in ["material", "finish", "construction", "frame"]):
            return row.get_text(separator=" ", strip=True)[:120]

    # Pattern: "Material: Solid Brass" or "Finish: Brushed Nickel"
    match = re.search(
        r"(?:material|finish|frame|construction)[:\s]+([A-Za-z0-9 ,\-/&]+)",
        text,
        re.IGNORECASE,
    )
    return match.group(1).strip()[:80] if match else "N/A"


def extract_key_attributes(soup: BeautifulSoup) -> dict:
    """
    Extract a key:value dictionary of product specifications from any
    spec table, definition list, or labeled list on the page.
    """
    attributes: dict = {}

    # Strategy 1: HTML <table> spec tables (very common)
    for table in soup.select("table"):
        for row in table.select("tr"):
            cells = [td.get_text(separator=" ", strip=True) for td in row.select("td, th")]
            if len(cells) == 2:
                key, val = cells
                if key and val and len(key) < 60:
                    attributes[key] = val[:120]

    # Strategy 2: <dl> definition lists
    for dl in soup.select("dl"):
        terms = dl.select("dt")
        defs = dl.select("dd")
        for dt, dd in zip(terms, defs):
            key = dt.get_text(strip=True)
            val = dd.get_text(separator=" ", strip=True)
            if key and val:
                attributes[key] = val[:120]

    # Strategy 3: labeled list items "Key: Value"
    if not attributes:
        for item in soup.select("li, .spec-item, [class*='spec-row'], [class*='attribute']"):
            text = item.get_text(separator=" ", strip=True)
            if ":" in text and len(text) < 160:
                parts = text.split(":", 1)
                key, val = parts[0].strip(), parts[1].strip()
                if key and val and len(key) < 60:
                    attributes[key] = val[:120]

    # Cap at 30 attributes to keep JSON readable
    return dict(list(attributes.items())[:30])


def find_image_url(soup: BeautifulSoup, base_url: str) -> str:
    """Find the primary product image URL."""
    # Open Graph image (most reliable)
    og = soup.select_one('meta[property="og:image"]')
    if og and og.get("content"):
        return urljoin(base_url, og["content"])

    # Structured data
    sd = soup.select_one('[itemprop="image"]')
    if sd:
        src = sd.get("src") or sd.get("content")
        if src:
            return urljoin(base_url, src)

    # Largest <img> heuristic
    for img in soup.select("img.product-image, img.main-image, #main-image, .pdp-image img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if src:
            return urljoin(base_url, src)

    # Fallback: first reasonably large image
    for img in soup.select("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if src and not src.startswith("data:"):
            return urljoin(base_url, src)

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Image download
# ─────────────────────────────────────────────────────────────────────────────


def download_image(image_url: str, dest_path: Path, timeout: int = REQUEST_TIMEOUT) -> bool:
    """Download an image to dest_path. Returns True on success."""
    if not image_url:
        return False
    try:
        resp = requests.get(image_url, headers=DEFAULT_HEADERS, timeout=timeout, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if "image" not in content_type and "octet-stream" not in content_type:
            print(f"  ⚠  Skipping non-image content-type: {content_type}")
            return False
        with open(dest_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                fh.write(chunk)
        return True
    except Exception as exc:
        print(f"  ⚠  Image download failed: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Core scrape function
# ─────────────────────────────────────────────────────────────────────────────


def scrape_product(url: str, timeout: int = REQUEST_TIMEOUT) -> dict:
    """
    Fetch a product URL and extract structured data.
    Returns a dict with keys: title, price, dimensions, material,
    key_attributes, image_url, source_url, scraped_at.
    """
    print(f"  → Fetching: {url}")
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        sys.exit(f"Error: Request timed out after {timeout}s. Check your internet connection.")
    except requests.exceptions.TooManyRedirects:
        sys.exit("Error: Too many redirects. The URL may be invalid.")
    except requests.exceptions.HTTPError as exc:
        sys.exit(f"Error: HTTP {exc.response.status_code} — {exc}")
    except requests.exceptions.ConnectionError:
        sys.exit("Error: Could not connect. Check the URL and your internet connection.")
    except requests.exceptions.RequestException as exc:
        sys.exit(f"Error: {exc}")

    soup = BeautifulSoup(resp.text, "lxml")

    title = extract_title(soup, url)
    price = extract_price(soup)
    dimensions = extract_dimensions(soup)
    material = extract_material(soup)
    key_attributes = extract_key_attributes(soup)
    image_url = find_image_url(soup, url)

    return {
        "title": title,
        "price": price,
        "dimensions": dimensions,
        "material": material,
        "key_attributes": key_attributes,
        "image_url": image_url,
        "source_url": url,
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "notes": "",
        "warranty": "",
        "pros": [],
        "cons": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Save to vault
# ─────────────────────────────────────────────────────────────────────────────


def save_to_vault(
    data: dict,
    category: str,
    name_override: str | None = None,
    save_image: bool = True,
) -> Path:
    """
    Save product data JSON (and optionally image) to vault/<category>/.
    Returns the path to the saved JSON file.
    """
    category_dir = VAULT_ROOT / category
    category_dir.mkdir(parents=True, exist_ok=True)

    # Determine file name
    base_name = slugify(name_override or data["title"])
    if not base_name:
        base_name = hashlib.md5(data["source_url"].encode()).hexdigest()[:12]

    json_path = category_dir / f"{base_name}.json"

    # Save image
    if save_image and data.get("image_url"):
        ext = Path(urlparse(data["image_url"]).path).suffix or ".jpg"
        ext = ext[:5]  # guard against bizarre extensions
        image_path = category_dir / f"{base_name}{ext}"
        if download_image(data["image_url"], image_path):
            data["image_local"] = str(image_path.relative_to(VAULT_ROOT.parent))
            print(f"  ✓ Image saved:  {image_path}")
        else:
            data["image_local"] = None
    else:
        data["image_local"] = None

    # Write JSON
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

    return json_path


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="HomeLogic Product Capture — scrape a product URL into your vault.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--url", required=True, help="Product page URL to scrape")
    parser.add_argument(
        "--category",
        required=True,
        help="Vault category (e.g. fans, lighting, hardware, flooring, cabinet_storage)",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Override the auto-detected product name (used as filename)",
    )
    parser.add_argument(
        "--no-image",
        action="store_true",
        help="Skip downloading the product image",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=REQUEST_TIMEOUT,
        help=f"HTTP request timeout in seconds (default: {REQUEST_TIMEOUT})",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Validate category against config
    config = load_config()
    valid_categories = config.get("vault_categories", [])
    if valid_categories and args.category not in valid_categories:
        print(
            f"⚠  Category '{args.category}' is not in config.yaml.\n"
            f"   Known categories: {', '.join(valid_categories)}\n"
            f"   Continuing anyway — the folder will be created."
        )

    print(f"\n🔍 Capturing product from: {args.url}")
    print(f"   Category: {args.category}")

    data = scrape_product(args.url, timeout=args.timeout)

    print(f"  ✓ Title:      {data['title']}")
    print(f"  ✓ Price:      {data['price']}")
    print(f"  ✓ Dimensions: {data['dimensions']}")
    print(f"  ✓ Material:   {data['material']}")
    print(f"  ✓ Attributes: {len(data['key_attributes'])} extracted")

    json_path = save_to_vault(
        data,
        category=args.category,
        name_override=args.name,
        save_image=not args.no_image,
    )

    print(f"\n✅ Saved to: {json_path}\n")


if __name__ == "__main__":
    main()
