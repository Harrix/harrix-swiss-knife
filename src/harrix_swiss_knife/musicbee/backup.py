"""Copy MusicBee library files and export `.m3u8` dumps before edits."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from harrix_swiss_knife.musicbee.mbp import parse_mbp, tracks_to_m3u8

if TYPE_CHECKING:
    from pathlib import Path


def create_musicbee_backup(library_dir: Path, backup_root: Path) -> Path:
    """Copy playlists and the library file into a timestamped backup folder."""
    stamp = datetime.now(UTC).astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    destination = backup_root / "MusicBee" / stamp
    destination.mkdir(parents=True, exist_ok=True)
    playlists_dir = library_dir / "Playlists"
    if playlists_dir.is_dir():
        shutil.copytree(playlists_dir, destination / "Playlists", dirs_exist_ok=True)
    for name in ("MusicBeeLibrary.mbl", "MusicBeeLibrary.bak", "MusicBeeLibrary.pfidx"):
        source = library_dir / name
        if source.is_file():
            shutil.copy2(source, destination / name)
    _export_m3u8(playlists_dir, destination / "exported")
    return destination


def _export_m3u8(playlists_dir: Path, export_dir: Path) -> None:
    if not playlists_dir.is_dir():
        return
    export_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(playlists_dir.glob("*.mbp")):
        try:
            playlist = parse_mbp(path)
        except ValueError:
            continue
        (export_dir / f"{path.stem}.m3u8").write_text(tracks_to_m3u8(playlist.tracks), encoding="utf-8")
