"""Resolve missing MusicBee paths to files under the music root."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from harrix_swiss_knife.musicbee.paths import normalize_path_key

if TYPE_CHECKING:
    from harrix_swiss_knife.musicbee.index import FileIndex, IndexedFile


@dataclass(frozen=True, slots=True)
class PathMatch:
    """Outcome of looking up a missing library or playlist path."""

    original: str
    status: str
    resolved: str | None = None
    candidates: tuple[str, ...] = ()


def match_missing_path(original: str, index: FileIndex, *, file_size: int | None = None) -> PathMatch:
    """Map `original` to a unique file under the music index.

    Status is `ok` (still present), `remap`, `ambiguous`, or `missing`.

    """
    existing = index.existing_path(original)
    if existing is not None:
        resolved = str(existing)
        if normalize_path_key(resolved) == normalize_path_key(original):
            return PathMatch(original=original, status="ok", resolved=resolved)
        return PathMatch(original=original, status="remap", resolved=resolved)

    basename = Path(original).name.casefold()
    hits = list(index.by_basename.get(basename, ()))
    if file_size is not None and len(hits) != 1:
        sized = [item for item in hits if item.size == file_size]
        if sized:
            hits = sized
    return _from_hits(original, hits)


def _from_hits(original: str, hits: list[IndexedFile]) -> PathMatch:
    if len(hits) == 1:
        return PathMatch(original=original, status="remap", resolved=str(hits[0].path))
    if len(hits) > 1:
        return PathMatch(
            original=original,
            status="ambiguous",
            candidates=tuple(str(item.path) for item in hits),
        )
    return PathMatch(original=original, status="missing")
