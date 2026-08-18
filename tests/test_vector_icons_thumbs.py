"""Tests for Vector Icons disk thumbnail freshness."""

from __future__ import annotations

import json
from pathlib import Path

from harrix_swiss_knife.apps.icons.catalog import IconFamily
from harrix_swiss_knife.apps.icons.thumb_cache import THUMB_FORMAT_VERSION, ThumbnailCache


def _family(family_id: str, featured_hash: str) -> IconFamily:
    return IconFamily(
        id=family_id,
        title=family_id,
        categories=[],
        tags=[],
        folder="",
        featured=f"{family_id}.svg",
        featured_hash=featured_hash,
    )


def test_stale_families_reuses_matching_disk_thumbs(tmp_path: Path) -> None:
    fresh = _family("building__garage", "abc")
    stale_hash = _family("building__house", "old")
    missing = _family("building__shop", "xyz")
    (tmp_path / f"{fresh.id}.png").write_bytes(b"png")
    (tmp_path / f"{stale_hash.id}.png").write_bytes(b"png")
    (tmp_path / "meta.json").write_text(
        json.dumps(
            {
                fresh.id: {"hash": "abc", "size": 160, "format": THUMB_FORMAT_VERSION},
                stale_hash.id: {"hash": "new", "size": 160, "format": THUMB_FORMAT_VERSION},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    cache = ThumbnailCache(cache_dir=tmp_path, size=160)
    assert cache.is_fresh(fresh)
    assert cache.stale_families([fresh, stale_hash, missing]) == [stale_hash, missing]
