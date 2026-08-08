"""Per-device sync index stored under `path_photos/.hsk-photo-sync/`."""

from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

_DEVICE_ID_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


class DeviceSyncIndex:
    """Thread-safe JSON index: mediaId → hash + filename (relative path)."""

    def __init__(self, photos_dir: Path, device_id: str) -> None:
        """Load or create the index file for `device_id` under `photos_dir`."""
        self._photos_dir = photos_dir
        self._device_id = _sanitize_device_id(device_id)
        self._path = photos_dir / ".hsk-photo-sync" / f"{self._device_id}.json"
        self._lock = threading.Lock()
        self._entries: dict[str, IndexEntry] = {}
        self._load()

    def get(self, media_id: str) -> IndexEntry | None:
        """Return the index entry for `media_id`, if any."""
        with self._lock:
            return self._entries.get(str(media_id))

    def known_hashes(self) -> set[str]:
        """Return all content hashes currently recorded for this device."""
        with self._lock:
            return {entry.content_hash for entry in self._entries.values()}

    def needed_media_ids(
        self,
        items: list[dict[str, Any]],
        *,
        find_existing_hash: Callable[[str], str | None] | None = None,
    ) -> list[str]:
        """Return mediaIds whose content is not already present.

        A photo is skipped when:

        - the device index already maps `mediaId` to the same hash and the file
          still exists (anywhere under `path_photos`, including subfolders), or
        - `find_existing_hash` finds the same content hash anywhere in the library.

        Matching library hits are recorded in the device index so later edits of
        the same MediaStore ID can still overwrite the sorted location.

        """
        needed: list[str] = []
        dirty = False
        with self._lock:
            for item in items:
                media_id = str(item.get("mediaId", "")).strip()
                content_hash = str(item.get("contentHash", "")).strip().lower()
                if not media_id or not content_hash:
                    continue
                existing = self._entries.get(media_id)
                if (
                    existing is not None
                    and existing.content_hash.lower() == content_hash
                    and (self._photos_dir / existing.filename).is_file()
                ):
                    continue
                found = find_existing_hash(content_hash) if find_existing_hash is not None else None
                if found:
                    changed = (
                        existing is None or existing.content_hash.lower() != content_hash or existing.filename != found
                    )
                    if changed:
                        self._entries[media_id] = IndexEntry(content_hash=content_hash, filename=found)
                        dirty = True
                    continue
                needed.append(media_id)
            if dirty:
                self._save_unlocked()
        return needed

    def upsert(self, media_id: str, *, content_hash: str, filename: str) -> None:
        """Insert or update a mapping and persist to disk."""
        with self._lock:
            self._entries[str(media_id)] = IndexEntry(content_hash=content_hash, filename=filename)
            self._save_unlocked()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        items = raw.get("items") if isinstance(raw, dict) else None
        if not isinstance(items, dict):
            return
        for media_id, value in items.items():
            if not isinstance(value, dict):
                continue
            content_hash = str(value.get("contentHash", "")).strip()
            filename = str(value.get("filename", "")).strip().replace("\\", "/")
            if content_hash and filename:
                self._entries[str(media_id)] = IndexEntry(content_hash=content_hash, filename=filename)

    def _save_unlocked(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "deviceId": self._device_id,
            "items": {
                media_id: {"contentHash": entry.content_hash, "filename": entry.filename}
                for media_id, entry in sorted(self._entries.items())
            },
        }
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self._path)


@dataclass
class IndexEntry:
    """One synced photo mapping."""

    content_hash: str
    filename: str


def _sanitize_device_id(device_id: str) -> str:
    cleaned = _DEVICE_ID_SAFE.sub("_", device_id.strip()) or "unknown"
    return cleaned[:128]
