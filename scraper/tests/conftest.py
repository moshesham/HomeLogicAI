from __future__ import annotations

# Make the scraper package importable when pytest runs from the scraper/ dir.
import os
import sys
from pathlib import Path

# Add the repo root to sys.path so `import scraper.*` resolves to the package.
_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Use a writable temp dir for the file cache during tests.
os.environ.setdefault("SCRAPE_CACHE_DIR", "/tmp/scraper_test_cache")
