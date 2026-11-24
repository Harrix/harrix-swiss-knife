"""Paths for Beat Saber local saves and HSK backup ZIPs."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from harrix_swiss_knife.backup_paths import beat_saber_backup_root as _beat_saber_backup_root

_QUEST_PACKAGE = "com.beatgames.beatsaber"
_QUEST_FILES_REL = f"Android/data/{_QUEST_PACKAGE}/files"


def beat_saber_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return `{path_backups}/BeatSaber`, creating it when missing."""
    return _beat_saber_backup_root(config, config_path=config_path)


def default_export_zip_path(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return a timestamped ZIP path under the Beat Saber backup root."""
    stamp = datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S")
    return beat_saber_backup_root(config, config_path=config_path) / f"beat-saber-{stamp}.zip"


def pc_saves_dir() -> Path:
    r"""Return ``%USERPROFILE%\AppData\LocalLow\Hyperbolic Magnetism\Beat Saber``."""
    return Path.home() / "AppData" / "LocalLow" / "Hyperbolic Magnetism" / "Beat Saber"


def quest_remote_files_dir() -> str:
    """Return the Quest remote path for Beat Saber ``files`` (sdcard style)."""
    return f"/sdcard/{_QUEST_FILES_REL}"
