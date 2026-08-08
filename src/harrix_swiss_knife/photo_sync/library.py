"""Recursive photo library under `path_photos` for content-hash lookups."""

from __future__ import annotations

import hashlib
import json
import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

_IMAGE_SUFFIXES = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".heic",
        ".heif",
        ".gif",
        ".bmp",
        ".tif",
        ".tiff",
    }
)
_SYNC_META_DIR = ".hsk-photo-sync"
_CHUNK_SIZE = 1024 * 1024


class PhotosLibrary:
    """Index image files under `photos_dir` (all subfolders) by SHA-256.

    New sync uploads still write into the root of `photos_dir`; this catalog is
    only used to detect content that already exists anywhere in the tree.

    """

    def __init__(self, photos_dir: Path) -> None:
        """Create a library scanner for `photos_dir`."""
        self._photos_dir = photos_dir
        self._cache_path = photos_dir / _SYNC_META_DIR / "library-hashes.json"
        self._lock = threading.Lock()
        self._by_hash: dict[str, str] = {}
        self._file_cache: dict[str, dict[str, Any]] = {}
        self._load_cache()

    def find_relative_path(self, content_hash: str) -> str | None:
        """Return a relative path (POSIX-ish) for `content_hash`, if any."""
        key = content_hash.strip().lower()
        if not key:
            return None
        with self._lock:
            if not self._by_hash:
                self._refresh_unlocked()
            return self._by_hash.get(key)

    def refresh(self) -> None:
        """Rescan the tree and refresh hash → relative-path mappings."""
        with self._lock:
            self._refresh_unlocked()

    def remember(self, relative_path: str, content_hash: str) -> None:
        """Record a just-written file without a full rescan."""
        rel = _normalize_rel(relative_path)
        digest = content_hash.strip().lower()
        if not rel or not digest:
            return
        path = self._photos_dir / rel
        try:
            stat = path.stat()
        except OSError:
            return
        with self._lock:
            self._file_cache[rel] = {
                "size": stat.st_size,
                "mtime_ns": getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000)),
                "hash": digest,
            }
            self._by_hash[digest] = rel
            self._save_cache_unlocked()

    def _load_cache(self) -> None:
        if not self._cache_path.is_file():
            return
        try:
            raw = json.loads(self._cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        files = raw.get("files") if isinstance(raw, dict) else None
        if not isinstance(files, dict):
            return
        loaded: dict[str, dict[str, Any]] = {}
        for rel, value in files.items():
            if not isinstance(value, dict):
                continue
            digest = str(value.get("hash", "")).strip().lower()
            if not digest:
                continue
            loaded[_normalize_rel(str(rel))] = {
                "size": value.get("size"),
                "mtime_ns": value.get("mtime_ns"),
                "hash": digest,
            }
        self._file_cache = loaded

    def _refresh_unlocked(self) -> None:
        photos_dir = self._photos_dir
        if not photos_dir.is_dir():
            self._by_hash = {}
            self._file_cache = {}
            return

        next_cache: dict[str, dict[str, Any]] = {}
        by_hash: dict[str, str] = {}
        candidates = sorted(
            (path for path in photos_dir.rglob("*") if path.is_file()),
            key=lambda item: item.as_posix().lower(),
        )
        for path in candidates:
            if path.suffix.lower() not in _IMAGE_SUFFIXES:
                continue
            if path.name.endswith(".partial"):
                continue
            try:
                relative = path.relative_to(photos_dir)
            except ValueError:
                continue
            if _SYNC_META_DIR in relative.parts:
                continue
            rel = relative.as_posix()
            try:
                stat = path.stat()
            except OSError:
                continue
            mtime_ns = getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000))
            size = stat.st_size
            cached = self._file_cache.get(rel)
            if (
                cached is not None
                and cached.get("size") == size
                and cached.get("mtime_ns") == mtime_ns
                and isinstance(cached.get("hash"), str)
            ):
                digest = str(cached["hash"]).lower()
            else:
                digest = _sha256_file(path)
            next_cache[rel] = {"size": size, "mtime_ns": mtime_ns, "hash": digest}
            # Prefer the first path in sorted order when duplicates share a hash.
            by_hash.setdefault(digest, rel)

        self._file_cache = next_cache
        self._by_hash = by_hash
        self._save_cache_unlocked()

    def _save_cache_unlocked(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"files": dict(sorted(self._file_cache.items()))}
        tmp = self._cache_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self._cache_path)


def _normalize_rel(relative_path: str) -> str:
    return relative_path.replace("\\", "/").lstrip("/")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(_CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()
