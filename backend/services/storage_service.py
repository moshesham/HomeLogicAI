from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from core.config import settings


def _storage_root() -> Path:
    return Path(settings.storage_path).resolve()


def get_project_path(project_id: str) -> Path:
    return _storage_root() / project_id


def get_room_path(project_id: str, room_id: str) -> Path:
    return get_project_path(project_id) / "rooms" / room_id


def get_category_path(project_id: str, room_id: str, category_id: str) -> Path:
    return get_room_path(project_id, room_id) / "categories" / category_id


def get_product_path(
    project_id: str, room_id: str, category_id: str, product_id: str
) -> Path:
    return (
        get_category_path(project_id, room_id, category_id)
        / "products"
        / f"{product_id}.json"
    )


def ensure_folder_structure(project_id: str, room_id: str, category_id: str) -> None:
    category_path = get_category_path(project_id, room_id, category_id)
    (category_path / "products").mkdir(parents=True, exist_ok=True)


def write_product_json(product: dict[str, Any]) -> None:
    project_id = str(product["project_id"])
    room_id = str(product["room_id"])
    category_id = str(product["category_id"])
    product_id = str(product["id"])

    ensure_folder_structure(project_id, room_id, category_id)
    product_path = get_product_path(project_id, room_id, category_id, product_id)
    product_path.write_text(
        json.dumps(product, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def read_product_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_notes(category_path: Path, content: str) -> None:
    category_path.mkdir(parents=True, exist_ok=True)
    notes_path = category_path / "notes.md"
    notes_path.write_text(content, encoding="utf-8")


def read_notes(category_path: Path) -> str:
    notes_path = category_path / "notes.md"
    if not notes_path.exists():
        return ""
    return notes_path.read_text(encoding="utf-8")


def delete_project_folder(project_id: str) -> None:
    project_path = get_project_path(project_id)
    if project_path.exists():
        shutil.rmtree(project_path)
