"""Copy / move / trash operations for Media Sorter bins."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QFile

from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import unique_path_in_folder
from harrix_swiss_knife.apps.media_sorter.database_manager import DatabaseManager, normalize_media_path

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class BinConfig:
    """Destination bin from `config.json`."""

    id: str
    title: str
    path: Path
    mode: str  # copy | move


@dataclass(slots=True)
class SortResult:
    """Outcome of assigning a file to a bin."""

    ok: bool
    source_path: str
    dest_path: str | None
    effective_mode: str
    error: str | None = None


def assign_to_bin(
    source: str | Path,
    bin_config: BinConfig,
    db: DatabaseManager,
) -> SortResult:
    """Copy or move `source` into `bin_config`, record assignment, mark reviewed.

    If the configured mode is `move` but the file was already moved earlier in this
    session/history and only a copy remains at the tracked path, subsequent bins
    copy from the current path (per product decision).

    """
    source_path = resolve_working_path(source, db)
    if not source_path.is_file():
        return SortResult(
            ok=False,
            source_path=str(source_path),
            dest_path=None,
            effective_mode=bin_config.mode,
            error=f"File not found: {source_path}",
        )

    dest_dir = bin_config.path
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return SortResult(
            ok=False,
            source_path=str(source_path),
            dest_path=None,
            effective_mode=bin_config.mode,
            error=f"Cannot create destination folder: {exc}",
        )

    dest_path = unique_path_in_folder(dest_dir, source_path.stem, source_path.suffix)
    # After any prior move of this file, later bins always copy (even if mode is move).
    effective_mode = bin_config.mode
    if effective_mode == "move" and db.path_was_moved(source_path):
        effective_mode = "copy"

    try:
        if effective_mode == "move":
            shutil.move(str(source_path), str(dest_path))
        else:
            shutil.copy2(str(source_path), str(dest_path))
    except OSError as exc:
        logger.exception("Failed to %s %s -> %s", effective_mode, source_path, dest_path)
        return SortResult(
            ok=False,
            source_path=str(source_path),
            dest_path=None,
            effective_mode=effective_mode,
            error=str(exc),
        )

    history_path = normalize_media_path(source_path)
    if not db.add_bin_assignment(history_path, bin_config.id, dest_path, effective_mode):
        return SortResult(
            ok=False,
            source_path=str(source_path),
            dest_path=str(dest_path),
            effective_mode=effective_mode,
            error="File transferred but failed to record bin assignment",
        )

    db.mark_reviewed(history_path)
    if effective_mode == "move":
        db.mark_reviewed(dest_path)

    return SortResult(
        ok=True,
        source_path=str(source_path),
        dest_path=str(dest_path),
        effective_mode=effective_mode,
    )


def parse_bins_from_config(media_sorter: dict | None) -> list[BinConfig]:
    """Parse `media_sorter.bins` into validated bin configs (skips incomplete entries)."""
    if not media_sorter or not isinstance(media_sorter, dict):
        return []
    raw_bins = media_sorter.get("bins") or []
    if not isinstance(raw_bins, list):
        return []
    result: list[BinConfig] = []
    for item in raw_bins:
        if not isinstance(item, dict):
            continue
        bin_id = str(item.get("id") or "").strip()
        title = str(item.get("title") or bin_id).strip() or bin_id
        path_raw = str(item.get("path") or "").strip()
        mode = str(item.get("mode") or "copy").strip().lower()
        if not bin_id or not path_raw or path_raw.startswith("<YOUR_"):
            continue
        if mode not in {"copy", "move"}:
            mode = "copy"
        result.append(BinConfig(id=bin_id, title=title, path=Path(path_raw).expanduser(), mode=mode))
    return result


def resolve_working_path(path: str | Path, db: DatabaseManager | None) -> Path:
    """Return the on-disk path to use (follows move history when present)."""
    candidate = Path(normalize_media_path(path))
    if candidate.is_file():
        return candidate
    if db is None:
        return candidate
    moved = Path(db.get_current_path_after_moves(path))
    if moved.is_file():
        return moved
    return candidate


def trash_file(path: str | Path, db: DatabaseManager) -> tuple[bool, str | None]:
    """Move `path` to the OS Recycle Bin and record deletion."""
    file_path = resolve_working_path(path, db)
    if not file_path.is_file():
        return False, f"File not found: {file_path}"
    size: int | None
    try:
        size = file_path.stat().st_size
    except OSError:
        size = None
    ok, _trashed_path = QFile.moveToTrash(str(file_path))
    if not ok:
        return False, "moveToTrash failed"
    db.mark_deleted(file_path, size)
    return True, None
