"""Official Beat Saber song catalog seed."""

from __future__ import annotations

import json
from importlib import resources
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


def catalog_summary(songs: list[dict[str, Any]] | None = None) -> str:
    """Return a short human summary of catalog size."""
    items = songs if songs is not None else load_official_songs()
    packs = {str(item.get("pack") or "") for item in items}
    packs.discard("")
    return f"{len(items)} official songs across {len(packs)} packs"


def load_official_songs() -> list[dict[str, str]]:
    """Return seeded official songs as `{level_id, title, pack}` dicts."""
    package = resources.files("harrix_swiss_knife.beat_saber_saves")
    data_file = package.joinpath("data/official_songs.json")
    raw = data_file.read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, list):
        return []
    songs: list[dict[str, str]] = []
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        level_id = str(entry.get("level_id") or "").strip()
        if not level_id or level_id.startswith("custom_level_"):
            continue
        songs.append(
            {
                "level_id": level_id,
                "title": str(entry.get("title") or level_id).strip() or level_id,
                "pack": str(entry.get("pack") or "").strip(),
            }
        )
    return songs


def load_official_songs_from_path(path: Path) -> list[dict[str, str]]:
    """Load official songs from an explicit JSON path (tests)."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        return []
    return [entry for entry in payload if isinstance(entry, dict) and str(entry.get("level_id") or "").strip()]


def official_songs_as_rows() -> list[tuple[str, str, str]]:
    """Return `(level_id, title, pack)` tuples for DB seeding."""
    return [(s["level_id"], s["title"], s["pack"]) for s in load_official_songs()]
