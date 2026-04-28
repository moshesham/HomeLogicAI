#!/usr/bin/env python3
"""
compare.py — HomeLogic Comparison Engine
=========================================
Reads all JSON files in a vault subfolder and generates a comparison
table in Markdown or CSV format.

Usage:
    python compare/compare.py --folder vault/fans
    python compare/compare.py --folder vault/lighting --format csv
    python compare/compare.py --folder vault/hardware --output compare/kitchen_hardware.md
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Default columns for the comparison table
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_COLUMNS = ["name", "price", "warranty", "material", "dimensions", "notes"]

# Keys in the JSON that map to each column label
JSON_KEY_MAP = {
    "name": "title",
    "price": "price",
    "warranty": "warranty",
    "material": "material",
    "dimensions": "dimensions",
    "notes": "notes",
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def load_vault_items(folder: Path) -> list[dict]:
    """Load all JSON files in *folder* and return a list of product dicts."""
    items = []
    if not folder.exists():
        sys.exit(f"Error: Folder not found — {folder}")
    json_files = sorted(folder.glob("*.json"))
    if not json_files:
        sys.exit(f"No JSON files found in {folder}")
    for jf in json_files:
        try:
            with open(jf, encoding="utf-8") as fh:
                data = json.load(fh)
            data["_filename"] = jf.name
            items.append(data)
        except json.JSONDecodeError as exc:
            print(f"  ⚠  Skipping {jf.name}: invalid JSON ({exc})")
    return items


def get_cell(item: dict, column: str) -> str:
    """Extract a cell value for *column* from a product dict."""
    json_key = JSON_KEY_MAP.get(column, column)
    val = item.get(json_key, "")

    # Lists → comma-separated
    if isinstance(val, list):
        return ", ".join(str(v) for v in val) if val else ""

    # Dicts → JSON string (shouldn't happen for the default columns)
    if isinstance(val, dict):
        return json.dumps(val, ensure_ascii=False)

    return str(val).strip() if val is not None else ""


def pros_cons_cell(item: dict) -> str:
    """Build a combined pros/cons cell."""
    pros = item.get("pros", [])
    cons = item.get("cons", [])
    parts = []
    if pros:
        parts.append("✅ " + "; ".join(pros))
    if cons:
        parts.append("❌ " + "; ".join(cons))
    return " | ".join(parts) if parts else ""


# ─────────────────────────────────────────────────────────────────────────────
# Markdown renderer
# ─────────────────────────────────────────────────────────────────────────────


def _md_escape(text: str) -> str:
    """Escape pipe characters so Markdown tables don't break."""
    return text.replace("|", "\\|")


def render_markdown(items: list[dict], columns: list[str]) -> str:
    """Return a GitHub-flavored Markdown comparison table."""
    all_columns = columns + ["pros / cons"]

    # Header
    header = "| " + " | ".join(col.title() for col in all_columns) + " |"
    separator = "| " + " | ".join("---" for _ in all_columns) + " |"

    rows = [header, separator]

    for item in items:
        cells = []
        for col in columns:
            cells.append(_md_escape(get_cell(item, col)))
        cells.append(_md_escape(pros_cons_cell(item)))
        rows.append("| " + " | ".join(cells) + " |")

    return "\n".join(rows) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# CSV renderer
# ─────────────────────────────────────────────────────────────────────────────


def render_csv(items: list[dict], columns: list[str], output_path: Path) -> None:
    """Write a CSV comparison table to *output_path*."""
    all_columns = columns + ["pros_cons"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=all_columns)
        writer.writeheader()
        for item in items:
            row = {col: get_cell(item, col) for col in columns}
            row["pros_cons"] = pros_cons_cell(item)
            writer.writerow(row)
    print(f"✅ CSV saved: {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Config loader
# ─────────────────────────────────────────────────────────────────────────────


def load_columns_from_config() -> list[str]:
    """Try to load column preferences from config.yaml."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        try:
            import yaml

            with open(config_path) as fh:
                cfg = yaml.safe_load(fh) or {}
            return cfg.get("compare", {}).get("columns", DEFAULT_COLUMNS)
        except Exception:
            pass
    return DEFAULT_COLUMNS


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="HomeLogic Comparison Engine — compare products in a vault folder.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--folder",
        required=True,
        help="Path to a vault subfolder (e.g. vault/fans)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "csv"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path. Defaults to <folder>/comparison.md or comparison.csv",
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        default=None,
        help=(
            "Columns to include (default from config.yaml or: "
            + " ".join(DEFAULT_COLUMNS)
            + ")"
        ),
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    folder = Path(args.folder)
    columns = args.columns or load_columns_from_config()
    fmt = args.format

    items = load_vault_items(folder)
    print(f"📦 Found {len(items)} item(s) in {folder}")

    if fmt == "markdown":
        md = render_markdown(items, columns)

        if args.output:
            out_path = Path(args.output)
        else:
            out_path = folder / "comparison.md"

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(f"# Comparison: {folder.name.replace('_', ' ').title()}\n\n")
            fh.write(md)
        print(f"✅ Markdown saved: {out_path}")

        # Also print to stdout
        print()
        print(md)

    elif fmt == "csv":
        if args.output:
            out_path = Path(args.output)
        else:
            out_path = folder / "comparison.csv"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        render_csv(items, columns, out_path)


if __name__ == "__main__":
    main()
