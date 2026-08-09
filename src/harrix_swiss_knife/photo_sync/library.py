"""Recursive photo library under `path_photos` for content-hash lookups."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

logger = logging.getLogger(__name__)

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
# Windows: cloud placeholders (Dropbox / OneDrive) — reading them can hang or hydrate.
_FILE_ATTRIBUTE_OFFLINE = 0x1000
_FILE_ATTRIBUTE_RECALL_ON_OPEN = 0x40000
_FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x400000
_CLOUD_PLACEHOLDER_ATTRS = (
    _FILE_ATTRIBUTE_OFFLINE | _FILE_ATTRIBUTE_RECALL_ON_OPEN | _FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS
)
_DEFAULT_MAX_AGE_SEC = 120.0


class PhotosLibrary:
    """Index image files under `photos_dir` (all subfolders) by SHA-256.

    New sync uploads still write into the root of `photos_dir`; this catalog is
    only used to detect content that already exists anywhere in the tree.

    """

    def __init__(self, photos_dir: Path) -> None:
        """Create a library scanner for `photos_dir`.

        Disk cache is not loaded here: on cloud folders (Dropbox) that I/O can
        block the UI thread for a long time. Load happens lazily off the UI path
        via `refresh` / `ensure_fresh` / first lookup.

        """
        self._photos_dir = photos_dir
        self._cache_path = photos_dir / _SYNC_META_DIR / "library-hashes.json"
        self._lock = threading.Lock()
        self._by_hash: dict[str, str] = {}
        self._file_cache: dict[str, dict[str, Any]] = {}
        self._last_refresh_at: float | None = None
        self._disk_cache_loaded = False

    def ensure_fresh(self, *, max_age_sec: float = _DEFAULT_MAX_AGE_SEC) -> None:
        """Refresh only when the index is missing or older than `max_age_sec`."""
        with self._lock:
            self._ensure_disk_cache_loaded_unlocked()
            if self._last_refresh_at is not None and (time.monotonic() - self._last_refresh_at) < max_age_sec:
                return
            self._refresh_unlocked()

    def find_relative_path(self, content_hash: str) -> str | None:
        """Return a relative path (POSIX-ish) for `content_hash`, if any."""
        key = content_hash.strip().lower()
        if not key:
            return None
        with self._lock:
            self._ensure_disk_cache_loaded_unlocked()
            if not self._by_hash and self._last_refresh_at is None:
                self._refresh_unlocked()
            return self._by_hash.get(key)

    def refresh(self) -> None:
        """Rescan the tree and refresh hash → relative-path mappings."""
        with self._lock:
            self._ensure_disk_cache_loaded_unlocked()
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

    @property
    def unique_hash_count(self) -> int:
        """Number of distinct content hashes currently indexed."""
        with self._lock:
            return len(self._by_hash)

    def warm_in_background(self, *, on_done: Callable[[], None] | None = None) -> None:
        """Start a daemon scan so the first phone manifest is less likely to time out."""

        def run() -> None:
            try:
                self.refresh()
            except Exception:
                logger.exception("Photo library background scan failed")
            if on_done is not None:
                try:
                    on_done()
                except Exception:
                    logger.exception("Photo library warm callback failed")

        threading.Thread(target=run, name="photo-sync-library-warm", daemon=True).start()

    def _ensure_disk_cache_loaded_unlocked(self) -> None:
        """Load `library-hashes.json` once. Caller must hold `_lock`."""
        if self._disk_cache_loaded:
            return
        self._load_cache()
        self._disk_cache_loaded = True

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
        by_hash: dict[str, str] = {}
        for rel, value in files.items():
            if not isinstance(value, dict):
                continue
            digest = str(value.get("hash", "")).strip().lower()
            if not digest:
                continue
            norm = _normalize_rel(str(rel))
            loaded[norm] = {
                "size": value.get("size"),
                "mtime_ns": value.get("mtime_ns"),
                "hash": digest,
            }
            by_hash.setdefault(digest, norm)
        self._file_cache = loaded
        self._by_hash = by_hash
        # Treat disk cache as a starting point; still refresh soon, but lookups work immediately.
        if by_hash:
            self._last_refresh_at = time.monotonic()

    def _refresh_unlocked(self) -> None:
        photos_dir = self._photos_dir
        if not photos_dir.is_dir():
            self._by_hash = {}
            self._file_cache = {}
            self._last_refresh_at = time.monotonic()
            return

        next_cache: dict[str, dict[str, Any]] = {}
        by_hash: dict[str, str] = {}
        skipped_cloud = 0
        for path in photos_dir.rglob("*"):
            if not path.is_file():
                continue
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
            if _is_cloud_placeholder(stat):
                skipped_cloud += 1
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
                try:
                    digest = _sha256_file(path)
                except OSError:
                    continue
            next_cache[rel] = {"size": size, "mtime_ns": mtime_ns, "hash": digest}
            # Prefer the first path when duplicates share a hash.
            by_hash.setdefault(digest, rel)

        self._file_cache = next_cache
        self._by_hash = by_hash
        self._last_refresh_at = time.monotonic()
        self._save_cache_unlocked()
        if skipped_cloud:
            logger.info("Photo library scan skipped %s cloud-only placeholder file(s)", skipped_cloud)

    def _save_cache_unlocked(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"files": dict(sorted(self._file_cache.items()))}
        tmp = self._cache_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self._cache_path)


def _is_cloud_placeholder(stat: Any) -> bool:
    """Return `True` for Windows cloud placeholders that must not be opened for hashing."""
    attrs = getattr(stat, "st_file_attributes", 0)
    if not isinstance(attrs, int) or attrs == 0:
        return False
    return bool(attrs & _CLOUD_PLACEHOLDER_ATTRS)


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
