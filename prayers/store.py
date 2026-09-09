"""Loading prayer documents from disk."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).parent / "data"


@lru_cache(maxsize=64)
def load(doc_id: str) -> dict:
    path = _DATA / f"{doc_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"No prayer document '{doc_id}'")
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def catalogue() -> dict[str, dict]:
    """Every document, by id — id, title, slot and estimated minutes."""
    out = {}
    for path in sorted(_DATA.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        out[doc["id"]] = doc
    return out


def by_slot(slot: str) -> list[dict]:
    return [d for d in catalogue().values() if d.get("slot") == slot]
