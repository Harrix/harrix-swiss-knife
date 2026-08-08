"""Filename allocation for synced photos."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

_MAX_EXTENSION_LEN = 8

_MIME_EXTENSIONS: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
    "image/heif": "heif",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
}


def allocate_filename(
    photos_dir: Path,
    *,
    date_taken_epoch_ms: int,
    extension: str,
    force_copy: bool,
    reuse_filename: str | None = None,
) -> str:
    """Choose a destination path relative to `photos_dir`.

    - If `reuse_filename` is set (same MediaStore ID, content changed), keep it
      even when it points into a subfolder (overwrite the sorted copy).
    - Otherwise allocate a **root-only** name `yyyy-MM-dd HH.mm.ss.ext`, or
      `_copy` / `_copy2` / … when the root name is taken.

    """
    if reuse_filename:
        return reuse_filename.replace("\\", "/").lstrip("/")

    ext = extension.lstrip(".").lower() or "jpg"
    base = stem_from_date_taken_ms(date_taken_epoch_ms)
    if not force_copy:
        candidate = f"{base}.{ext}"
        if not (photos_dir / candidate).exists():
            return candidate

    # Collision or explicit copy: allocate _copy, _copy2, … in the root folder.
    index = 1
    while True:
        suffix = "_copy" if index == 1 else f"_copy{index}"
        candidate = f"{base}{suffix}.{ext}"
        if not (photos_dir / candidate).exists():
            return candidate
        index += 1


def display_name_prefers_copy(display_name: str | None) -> bool:
    """Return `True` when the phone filename already looks like an edited copy."""
    if not display_name:
        return False
    stem = Path(display_name).stem
    return bool(re.search(r"_copy\d*$", stem, flags=re.IGNORECASE))


def extension_for_mime(mime_type: str | None, display_name: str | None = None) -> str:
    """Return a lowercase file extension without a leading dot."""
    if mime_type:
        mapped = _MIME_EXTENSIONS.get(mime_type.lower().strip())
        if mapped:
            return mapped
    if display_name and "." in display_name:
        ext = display_name.rsplit(".", 1)[-1].lower()
        if ext and ext.isalnum() and len(ext) <= _MAX_EXTENSION_LEN:
            return "jpg" if ext == "jpeg" else ext
    return "jpg"


def stem_from_date_taken_ms(date_taken_epoch_ms: int) -> str:
    """Format capture time as `yyyy-MM-dd HH.mm.ss` in the local timezone."""
    seconds = max(0, int(date_taken_epoch_ms)) / 1000.0
    local = datetime.fromtimestamp(seconds, tz=UTC).astimezone()
    return local.strftime("%Y-%m-%d %H.%M.%S")
