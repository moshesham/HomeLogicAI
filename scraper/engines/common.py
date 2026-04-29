from __future__ import annotations

import re
from decimal import Decimal
from typing import Any


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def parse_price(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"\$\s*([\d,]+(?:\.\d{1,2})?)", value)
    if not match:
        match = re.search(r"([\d,]+(?:\.\d{1,2})?)", value)
    if not match:
        return None
    raw = match.group(1).replace(",", "")
    try:
        return float(Decimal(raw))
    except Exception:
        return None


def normalize_spec_map(raw_specs: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in raw_specs.items():
        norm_key = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
        normalized[norm_key or key] = value
    return normalized
