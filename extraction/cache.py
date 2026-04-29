"""Disk-based cache for Gemini API extraction results.

Cache key is an MD5 hash of `prompt_version + content`. Each entry is stored as
UTF-8 JSON at `extraction_cache/{hash}.json`. The cache directory is committed to
the repo so re-runs across team members hit the same cache.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / "extraction_cache"


def make_cache_key(prompt_version: str, content: str) -> str:
    """Return the MD5 hex digest used as the cache filename stem."""
    payload = f"{prompt_version}{content}".encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def _cache_path(prompt_version: str, content: str) -> Path:
    return CACHE_DIR / f"{make_cache_key(prompt_version, content)}.json"


def get_cached(prompt_version: str, content: str) -> dict | None:
    """Return the cached extraction dict for this (version, content), or None."""
    path = _cache_path(prompt_version, content)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_to_cache(prompt_version: str, content: str, result: dict) -> None:
    """Persist `result` as UTF-8 JSON keyed by (prompt_version, content)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(prompt_version, content)
    with path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
