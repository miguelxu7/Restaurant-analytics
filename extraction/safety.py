"""Daily API call limit guard.

Keeps a running counter of Gemini calls made today, persisted at
`extraction_cache/.daily_limit.json`. The counter resets automatically when the
date changes. Limit is set conservatively under the Gemini 2.5 Flash-Lite free
tier (1000/day) with a 100-call buffer so we never accidentally blow past it.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

DAILY_LIMIT = 900
STATE_PATH = Path(__file__).resolve().parent.parent / "extraction_cache" / ".daily_limit.json"


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"date": date.today().isoformat(), "count": 0}
    with STATE_PATH.open("r", encoding="utf-8") as f:
        state = json.load(f)
    if state.get("date") != date.today().isoformat():
        return {"date": date.today().isoformat(), "count": 0}
    return state


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_calls_today() -> int:
    """Return the number of API calls already made today."""
    return _load_state()["count"]


def check_and_increment() -> None:
    """Increment today's call counter, raising if the daily limit is hit.

    Raises:
        RuntimeError: if the call would exceed `DAILY_LIMIT`.
    """
    state = _load_state()
    if state["count"] >= DAILY_LIMIT:
        raise RuntimeError(
            f"Daily Gemini API limit reached ({DAILY_LIMIT} calls). "
            f"Resets at midnight local time."
        )
    state["count"] += 1
    _save_state(state)
