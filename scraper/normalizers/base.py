from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseNormalizer(ABC):
    category_slug: str

    @abstractmethod
    def normalize(self, raw_specs: dict, retailer: str) -> dict:
        """Map raw retailer spec keys to canonical attribute schema keys."""

    def load_schema(self) -> dict:
        categories_dir = Path(__file__).resolve().parents[2] / "categories"
        schema_path = categories_dir / f"{self.category_slug}.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Missing category schema: {schema_path}")
        return json.loads(schema_path.read_text(encoding="utf-8"))


class SchemaAliasNormalizer(BaseNormalizer):
    def __init__(self, category_slug: str) -> None:
        self.category_slug = category_slug

    def normalize(self, raw_specs: dict[str, Any], retailer: str) -> dict[str, Any]:
        schema = self.load_schema()
        normalized: dict[str, Any] = {}

        for attr in schema.get("attributes", []):
            canonical = attr.get("key")
            aliases = [a.lower() for a in attr.get("retailer_aliases", {}).get(retailer, [])]
            if not canonical:
                continue

            match_value = None
            for key, value in raw_specs.items():
                key_l = str(key).lower().strip()
                if key_l == canonical or key_l in aliases:
                    match_value = value
                    break
            if match_value is not None:
                normalized[canonical] = match_value

        return normalized
