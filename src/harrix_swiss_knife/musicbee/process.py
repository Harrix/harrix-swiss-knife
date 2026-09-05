"""Scan, remap, apply Stream rules, and write MusicBee playlists/library."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from harrix_swiss_knife.musicbee.backup import create_musicbee_backup
from harrix_swiss_knife.musicbee.index import index_audio_files
from harrix_swiss_knife.musicbee.match import PathMatch, match_missing_path
from harrix_swiss_knife.musicbee.mbl import parse_mbl, write_mbl
from harrix_swiss_knife.musicbee.mbp import parse_mbp, write_mbp
from harrix_swiss_knife.musicbee.paths import normalize_path_key
from harrix_swiss_knife.musicbee.rules import apply_rules

if TYPE_CHECKING:
    from pathlib import Path

    from harrix_swiss_knife.musicbee.index import FileIndex
    from harrix_swiss_knife.musicbee.mbl import MblLibrary
    from harrix_swiss_knife.musicbee.mbp import MbpPlaylist
    from harrix_swiss_knife.musicbee.rules import RuleWarning
    from harrix_swiss_knife.musicbee.settings import MusicBeeSettings

_MUSICBEE_PROCESS = "MusicBee.exe"


@dataclass
class CheckPlan:
    """In-memory result of a MusicBee check, ready to report or apply."""

    settings: MusicBeeSettings
    backup_path: Path
    remaps: list[PathMatch] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    ambiguous: list[PathMatch] = field(default_factory=list)
    playlists: list[PlaylistChange] = field(default_factory=list)
    warnings: list[RuleWarning] = field(default_factory=list)
    library: MblLibrary | None = None
    library_changed: bool = False
    parsed_playlists: dict[str, MbpPlaylist] = field(default_factory=dict)
    unreadable_playlists: list[str] = field(default_factory=list)

    @property
    def has_writes(self) -> bool:
        """Whether Apply would write the library or any static playlist."""
        return self.library_changed or any(item.changed for item in self.playlists)


@dataclass
class PlaylistChange:
    """One static playlist that may be rewritten."""

    name: str
    path: Path
    original_tracks: list[str]
    new_tracks: list[str]

    @property
    def changed(self) -> bool:
        """Whether the track list differs after remaps and rules."""
        return [normalize_path_key(item) for item in self.original_tracks] != [
            normalize_path_key(item) for item in self.new_tracks
        ]


def apply_plan(plan: CheckPlan) -> list[Path]:
    """Write changed `.mbl` / `.mbp` files. Raises if MusicBee is running."""
    if is_musicbee_running():
        msg = "Close MusicBee before applying playlist or library changes"
        raise OSError(msg)
    written: list[Path] = []
    if plan.library is not None and plan.library_changed:
        write_bytes = write_mbl(plan.library)
        plan.library.path.write_bytes(write_bytes)
        written.append(plan.library.path)
        pfidx = plan.library.path.with_suffix(".pfidx")
        if pfidx.is_file():
            pfidx.unlink()
            written.append(pfidx)
    for change in plan.playlists:
        if not change.changed:
            continue
        parsed = plan.parsed_playlists[change.name]
        change.path.write_bytes(write_mbp(parsed, change.new_tracks))
        written.append(change.path)
    return written


def format_check_report(plan: CheckPlan) -> str:
    """Build the preview text shown before Apply."""
    lines = [
        f"Backup: {plan.backup_path}",
        f"Library: {plan.settings.library_dir}",
        f"Music: {plan.settings.music_root}",
        f"Stream: {plan.settings.stream_root}",
        "",
    ]
    if is_musicbee_running():
        lines.append("MusicBee is running. Close it before clicking Apply.")
        lines.append("")
    lines.append(f"Remapped paths: {len(plan.remaps)}")
    for item in plan.remaps:
        lines.append(f"  {item.original}")
        lines.append(f"    → {item.resolved}")
    lines.append("")
    lines.append(f"Missing (not remapped): {len(plan.missing)}")
    lines.extend(f"  {path}" for path in plan.missing)
    lines.append("")
    lines.append(f"Ambiguous (not remapped): {len(plan.ambiguous)}")
    for item in plan.ambiguous:
        lines.append(f"  {item.original}")
        lines.extend(f"    ? {candidate}" for candidate in item.candidates)
    if plan.unreadable_playlists:
        lines.append("")
        lines.append("Unreadable static playlists:")
        lines.extend(f"  {name}" for name in plan.unreadable_playlists)
    lines.append("")
    changed = [item for item in plan.playlists if item.changed]
    lines.append(f"Playlists to rewrite: {len(changed)}")
    lines.extend(f"  {item.name}: {len(item.original_tracks)} → {len(item.new_tracks)} tracks" for item in changed)
    if plan.library_changed:
        lines.append("Library file: path remaps will be written (play counts kept).")
    if plan.warnings:
        lines.append("")
        lines.append("Rule notes:")
        lines.extend(f"  {warning.message}" for warning in plan.warnings)
    if not plan.has_writes:
        lines.append("")
        lines.append("Nothing to apply.")
    else:
        lines.append("")
        lines.append("Click Apply to write the library and static playlists.")
        lines.append("Cancel closes without writing.")
        lines.append("Smart playlists (.xautopf) are not edited.")
        lines.append("Files under the music folder are not changed.")
    return "\n".join(lines)


def is_musicbee_running() -> bool:
    """Return whether `MusicBee.exe` is running on Windows."""
    if sys.platform != "win32":
        return False
    tasklist = shutil.which("tasklist")
    if not tasklist:
        return False
    result = subprocess.run(
        [tasklist, "/FI", f"IMAGENAME eq {_MUSICBEE_PROCESS}", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    return "musicbee.exe" in (result.stdout or "").casefold()


def run_check(settings: MusicBeeSettings, *, create_backup: bool = True) -> CheckPlan:
    """Backup, index files, remap missing paths, and apply Stream rules in memory."""
    backup_path = (
        create_musicbee_backup(settings.library_dir, settings.backup_dir)
        if create_backup
        else settings.backup_dir / "MusicBee" / "preview"
    )
    index = index_audio_files(settings.music_root, settings.audio_extensions)
    playlists, unreadable = _load_static_playlists(settings.playlists_dir)
    library = _load_library(settings.library_file)
    matches = _collect_matches(library, playlists, index)
    remaps = [item for item in matches if item.status == "remap" and item.resolved]
    remap_map = {normalize_path_key(item.original): item.resolved for item in remaps if item.resolved}
    library_changed = _apply_library_remaps(library, remap_map)
    working = {name: _remap_tracks(playlist.tracks, remap_map) for name, playlist in playlists.items()}
    warnings = apply_rules(
        working,
        settings.rules,
        placeholders=settings.placeholders,
        file_index=index,
    )
    changes = [
        PlaylistChange(
            name=name,
            path=playlists[name].path,
            original_tracks=list(playlists[name].tracks),
            new_tracks=working[name],
        )
        for name in playlists
    ]
    return CheckPlan(
        settings=settings,
        backup_path=backup_path,
        remaps=remaps,
        missing=sorted({item.original for item in matches if item.status == "missing"}),
        ambiguous=[item for item in matches if item.status == "ambiguous"],
        playlists=changes,
        warnings=warnings,
        library=library,
        library_changed=library_changed,
        parsed_playlists=playlists,
        unreadable_playlists=unreadable,
    )


def _apply_library_remaps(library: MblLibrary | None, remap_map: dict[str, str]) -> bool:
    if library is None or not remap_map:
        return False
    changed = False
    for track in library.tracks:
        mapped = remap_map.get(normalize_path_key(track.path))
        if mapped and mapped != track.path:
            track.path = mapped
            changed = True
    return changed


def _collect_matches(
    library: MblLibrary | None,
    playlists: dict[str, MbpPlaylist],
    index: FileIndex,
) -> list[PathMatch]:
    seen: set[str] = set()
    results: list[PathMatch] = []
    if library is not None:
        for track in library.tracks:
            key = normalize_path_key(track.path)
            if key in seen:
                continue
            seen.add(key)
            results.append(match_missing_path(track.path, index, file_size=track.file_size))
    for playlist in playlists.values():
        for path in playlist.tracks:
            key = normalize_path_key(path)
            if key in seen:
                continue
            seen.add(key)
            results.append(match_missing_path(path, index))
    return results


def _load_library(path: Path) -> MblLibrary | None:
    if not path.is_file():
        return None
    return parse_mbl(path)


def _load_static_playlists(playlists_dir: Path) -> tuple[dict[str, MbpPlaylist], list[str]]:
    loaded: dict[str, MbpPlaylist] = {}
    unreadable: list[str] = []
    if not playlists_dir.is_dir():
        return loaded, unreadable
    for path in sorted(playlists_dir.glob("*.mbp")):
        try:
            playlist = parse_mbp(path)
        except ValueError:
            unreadable.append(path.name)
            continue
        loaded[playlist.path.stem] = playlist
    return loaded, unreadable


def _remap_tracks(tracks: list[str], remap_map: dict[str, str]) -> list[str]:
    return [remap_map.get(normalize_path_key(path), path) for path in tracks]
