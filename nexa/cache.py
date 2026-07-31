"""
cache.py

Exact-match cache for Tier 1 routing decisions. If the LLM has already
figured out that "open chrome" -> {"skill": "open_app", "params": {"app_name": "Chrome"}},
there's no reason to burn another LLM call figuring that out again next time
you say the same thing.

This caches the ROUTING decision, not the skill's execution result — running
open_app still actually opens Chrome every time. We're just skipping the
"which skill and what params" reasoning step on repeats.

Normalization is intentionally simple (lowercase + collapse whitespace) —
this is EXACT matching. "open chrome" and "please open chrome for me" are
different cache entries. Recognizing those as the same thing needs semantic
(embedding-based) caching, which we'll add later once there's a skill
expensive enough to justify it.
"""

import hashlib
import json
from nexa.db import get_connection


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _hash(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode()).hexdigest()


def get_cached_decision(text: str) -> dict | None:
    """Returns the cached {"skill": ..., "params": ...} dict, or None on a miss."""
    conn = get_connection()
    row = conn.execute(
        "SELECT response FROM cache_exact WHERE command_hash = ?", (_hash(text),)
    ).fetchone()
    conn.close()
    return json.loads(row[0]) if row else None


def set_cached_decision(text: str, decision: dict) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO cache_exact (command_hash, raw_text, response) VALUES (?, ?, ?)",
        (_hash(text), text, json.dumps(decision)),
    )
    conn.commit()
    conn.close()
