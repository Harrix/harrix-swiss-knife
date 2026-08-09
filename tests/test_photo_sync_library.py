"""Tests for recursive photo library hash lookup."""

from __future__ import annotations

import hashlib
from pathlib import Path

from harrix_swiss_knife.photo_sync.index import DeviceSyncIndex
from harrix_swiss_knife.photo_sync.library import PhotosLibrary


def _write_jpg(path: Path, payload: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def test_library_finds_hash_in_subdirectory(tmp_path: Path) -> None:
    digest = _write_jpg(tmp_path / "2024" / "trip" / "a.jpg", b"jpeg-bytes-a")
    _write_jpg(tmp_path / "root.jpg", b"jpeg-bytes-root")
    library = PhotosLibrary(tmp_path)
    library.refresh()
    assert library.find_relative_path(digest) == "2024/trip/a.jpg"


def test_needed_skips_content_already_in_subfolder(tmp_path: Path) -> None:
    digest = _write_jpg(tmp_path / "sorted" / "x.jpg", b"same-photo-bytes")
    library = PhotosLibrary(tmp_path)
    library.refresh()
    index = DeviceSyncIndex(tmp_path, "device-1")
    needed = index.needed_media_ids(
        [{"mediaId": "42", "contentHash": digest}],
        find_existing_hash=library.find_relative_path,
    )
    assert needed == []
    entry = index.get("42")
    assert entry is not None
    assert entry.filename == "sorted/x.jpg"
    assert entry.content_hash == digest


def test_needed_requests_upload_when_hash_missing(tmp_path: Path) -> None:
    library = PhotosLibrary(tmp_path)
    library.refresh()
    index = DeviceSyncIndex(tmp_path, "device-1")
    needed = index.needed_media_ids(
        [{"mediaId": "7", "contentHash": "a" * 64}],
        find_existing_hash=library.find_relative_path,
    )
    assert needed == ["7"]


def test_ensure_fresh_reuses_recent_index(tmp_path: Path) -> None:
    digest = _write_jpg(tmp_path / "a.jpg", b"fresh-check")
    library = PhotosLibrary(tmp_path)
    library.refresh()
    assert library.unique_hash_count == 1
    # Second call within max_age should not clear the index.
    library.ensure_fresh(max_age_sec=60.0)
    assert library.find_relative_path(digest) == "a.jpg"
