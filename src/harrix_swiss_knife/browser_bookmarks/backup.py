"""Backup Chromium Bookmarks files before sync writes."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from harrix_swiss_knife.browser_bookmarks.paths import backup_root

if TYPE_CHECKING:
    from pathlib import Path


def create_bookmarks_backup(chrome_path: Path, yandex_path: Path) -> Path:
    """Copy both Bookmarks files (and `.bak` if present) into a timestamped folder."""
    stamp = datetime.now(UTC).astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    dest = backup_root() / stamp
    dest.mkdir(parents=True, exist_ok=True)
    _copy_side(chrome_path, dest / "chrome")
    _copy_side(yandex_path, dest / "yandex")
    return dest


def _copy_side(source: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    if source.is_file():
        shutil.copy2(source, dest_dir / "Bookmarks")
    sibling = source.parent / "Bookmarks.bak"
    if sibling.is_file():
        shutil.copy2(sibling, dest_dir / "Bookmarks.bak")
