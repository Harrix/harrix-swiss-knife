"""Index audio files under the MusicBee music root."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from harrix_swiss_knife.musicbee.paths import normalize_path_key, path_is_file_safe


@dataclass
class FileIndex:
    """Lookup tables for remapping missing playlist/library paths."""

    files: list[IndexedFile] = field(default_factory=list)
    by_basename: dict[str, list[IndexedFile]] = field(default_factory=dict)
    by_key: dict[str, IndexedFile] = field(default_factory=dict)

    def existing_path(self, path: str) -> Path | None:
        """Return the indexed file for `path` when it exists."""
        hit = self.by_key.get(normalize_path_key(path))
        if hit is not None:
            return hit.path
        candidate = Path(path)
        return candidate if path_is_file_safe(candidate) else None


@dataclass
class IndexedFile:
    """One audio file on disk."""

    path: Path
    size: int

    @property
    def basename_key(self) -> str:
        """Casefolded file name."""
        return self.path.name.casefold()


def index_audio_files(root: Path, extensions: frozenset[str]) -> FileIndex:
    """Walk `root` and collect audio files whose suffix is in `extensions`."""
    index = FileIndex()
    try:
        if not root.is_dir():
            return index
    except OSError:
        return index
    suffixes = {item if item.startswith(".") else f".{item}" for item in extensions}
    suffixes = {item.casefold() for item in suffixes}
    try:
        children = root.rglob("*")
    except OSError:
        return index
    try:
        for path in children:
            if not path_is_file_safe(path) or path.suffix.casefold() not in suffixes:
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            item = IndexedFile(path=path, size=size)
            index.files.append(item)
            index.by_basename.setdefault(item.basename_key, []).append(item)
            index.by_key[normalize_path_key(path)] = item
    except OSError:
        return index
    return index
