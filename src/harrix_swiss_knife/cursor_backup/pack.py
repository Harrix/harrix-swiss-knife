"""Zip selected Cursor profile parts into a dated backup archive."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path  # noqa: TC003
from typing import TYPE_CHECKING

from harrix_swiss_knife.cursor_backup.paths import (
    cursor_dot_dir,
    cursor_user_dir,
    discover_project_cursor_dirs,
    iter_dot_cursor_entries,
    json_safe,
)
from harrix_swiss_knife.integrations.http_download import DownloadCancelledError

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

_MANIFEST_NAME = "manifest.json"
_SKIPPED_PREVIEW_LIMIT = 20
_ZIP_STORED_SUFFIXES = {".vscdb", ".db", ".sqlite", ".sqlite3"}


class BackupPart(StrEnum):
    """Selectable Cursor backup sections."""

    USER = "cursor-user"
    DOT_CURSOR = "dot-cursor"
    EXTENSIONS = "dot-cursor-extensions"
    PROJECT_CURSOR = "project-cursor"


@dataclass(frozen=True)
class BackupResult:
    """Outcome of packing a Cursor backup ZIP."""

    zip_path: Path
    parts: tuple[BackupPart, ...]
    file_count: int
    byte_count: int
    skipped: tuple[str, ...] = ()
    project_cursor_dirs: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass
class _PackState:
    file_count: int = 0
    byte_count: int = 0
    skipped: list[str] = field(default_factory=list)
    project_cursor_dirs: list[str] = field(default_factory=list)


def estimate_part_sizes(
    parts: Iterable[BackupPart] | None = None,
) -> dict[BackupPart, int]:
    """Return approximate on-disk byte sizes for each backup part."""
    wanted = tuple(parts) if parts is not None else tuple(BackupPart)
    sizes: dict[BackupPart, int] = {}
    for part in wanted:
        if part is BackupPart.USER:
            sizes[part] = _directory_size(cursor_user_dir())
        elif part is BackupPart.DOT_CURSOR:
            sizes[part] = sum(_path_size(path) for path in iter_dot_cursor_entries())
        elif part is BackupPart.EXTENSIONS:
            sizes[part] = _directory_size(cursor_dot_dir() / "extensions")
        elif part is BackupPart.PROJECT_CURSOR:
            sizes[part] = sum(_directory_size(path) for path in discover_project_cursor_dirs())
    return sizes


def format_backup_report(result: BackupResult) -> str:
    """Return a short markdown-ish report for the result dialog."""
    size_mb = result.byte_count / (1024 * 1024)
    zip_mb = result.zip_path.stat().st_size / (1024 * 1024) if result.zip_path.is_file() else 0.0
    lines = [
        f"ZIP: `{result.zip_path}` ({zip_mb:.1f} MB)",
        f"Packed {result.file_count} file(s), {size_mb:.1f} MB source data.",
        "Parts:",
    ]
    lines.extend(f"- {PART_LABELS[part]}" for part in result.parts)
    if result.project_cursor_dirs:
        lines.append("Project `.cursor` folders:")
        lines.extend(f"- `{path}`" for path in result.project_cursor_dirs)
    if result.skipped:
        lines.append(f"Skipped {len(result.skipped)} path(s) (locked or unreadable).")
        lines.extend(f"- `{path}`" for path in result.skipped[:_SKIPPED_PREVIEW_LIMIT])
        if len(result.skipped) > _SKIPPED_PREVIEW_LIMIT:
            lines.append(f"- … and {len(result.skipped) - _SKIPPED_PREVIEW_LIMIT} more")
    if result.warnings:
        lines.extend(result.warnings)
    lines.append("")
    lines.append(
        "Restore: fully quit Cursor, then unpack over `%APPDATA%\\Cursor\\User`, "
        "`%USERPROFILE%\\.cursor`, and each project `.cursor` as needed."
    )
    return "\n".join(lines)


def pack_cursor_backup(
    output_zip: Path,
    parts: Iterable[BackupPart],
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BackupResult:
    """Write selected Cursor data into `output_zip` and return a summary."""
    selected = tuple(dict.fromkeys(parts))
    if not selected:
        msg = "No Cursor backup parts selected."
        raise ValueError(msg)

    output_zip = output_zip.expanduser().resolve()
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    state = _PackState()
    warnings: list[str] = []
    cancel = should_cancel or (lambda: False)

    try:
        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
            for part in selected:
                _raise_if_cancelled(cancel)
                _pack_part(archive, part, state, cancel=cancel)

            manifest = {
                "created_at": datetime.now(UTC).astimezone().isoformat(timespec="seconds"),
                "parts": [part.value for part in selected],
                "file_count": state.file_count,
                "byte_count": state.byte_count,
                "skipped": state.skipped,
                "project_cursor_dirs": state.project_cursor_dirs,
                "sources": {
                    "user": str(cursor_user_dir()),
                    "dot_cursor": str(cursor_dot_dir()),
                },
            }
            archive.writestr(_MANIFEST_NAME, json.dumps(json_safe(manifest), indent=2, ensure_ascii=False) + "\n")
    except DownloadCancelledError:
        if output_zip.is_file():
            output_zip.unlink(missing_ok=True)
        raise

    if state.skipped:
        warnings.append("Some files were skipped; close Cursor and re-run for a consistent chat DB copy.")

    return BackupResult(
        zip_path=output_zip,
        parts=selected,
        file_count=state.file_count,
        byte_count=state.byte_count,
        skipped=tuple(state.skipped),
        project_cursor_dirs=tuple(state.project_cursor_dirs),
        warnings=tuple(warnings),
    )


def parts_from_labels(labels: Iterable[str]) -> list[BackupPart]:
    """Map dialog checkbox labels to `BackupPart` values."""
    parts: list[BackupPart] = []
    for label in labels:
        part = LABEL_TO_PART.get(label)
        if part is not None and part not in parts:
            parts.append(part)
    return parts


def _compress_type(path: Path) -> int:
    name = path.name.casefold()
    if path.suffix.casefold() in _ZIP_STORED_SUFFIXES or name.endswith(("-wal", "-shm")):
        return zipfile.ZIP_STORED
    return zipfile.ZIP_DEFLATED


def _directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return _file_size(path)
    total = 0
    try:
        for child in path.rglob("*"):
            if child.is_file():
                total += _file_size(child)
    except OSError:
        return total
    return total


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _pack_directory(
    archive: zipfile.ZipFile,
    source: Path,
    arc_prefix: str,
    state: _PackState,
    *,
    cancel: Callable[[], bool],
) -> None:
    if not source.exists():
        return
    if source.is_file():
        _write_file(archive, source, f"{arc_prefix}/{source.name}".replace("\\", "/"), state)
        return
    try:
        files = [path for path in source.rglob("*") if path.is_file()]
    except OSError as exc:
        state.skipped.append(f"{source} ({exc})")
        return
    for file_path in files:
        _raise_if_cancelled(cancel)
        try:
            relative = file_path.relative_to(source).as_posix()
        except ValueError:
            state.skipped.append(str(file_path))
            continue
        _write_file(archive, file_path, f"{arc_prefix}/{relative}", state)


def _pack_part(
    archive: zipfile.ZipFile,
    part: BackupPart,
    state: _PackState,
    *,
    cancel: Callable[[], bool],
) -> None:
    if part is BackupPart.USER:
        _pack_directory(archive, cursor_user_dir(), "Cursor/User", state, cancel=cancel)
        return
    if part is BackupPart.DOT_CURSOR:
        for entry in iter_dot_cursor_entries():
            _raise_if_cancelled(cancel)
            arc = f"dot-cursor/{entry.name}"
            _pack_directory(archive, entry, arc, state, cancel=cancel)
        return
    if part is BackupPart.EXTENSIONS:
        _pack_directory(archive, cursor_dot_dir() / "extensions", "dot-cursor/extensions", state, cancel=cancel)
        return
    if part is BackupPart.PROJECT_CURSOR:
        for index, cursor_dir in enumerate(discover_project_cursor_dirs(), start=1):
            _raise_if_cancelled(cancel)
            project_root = cursor_dir.parent
            state.project_cursor_dirs.append(str(cursor_dir))
            safe_name = _safe_arc_name(project_root, index)
            _pack_directory(archive, cursor_dir, f"project-cursor/{safe_name}/.cursor", state, cancel=cancel)
            meta = {"project_root": str(project_root), "cursor_dir": str(cursor_dir)}
            archive.writestr(
                f"project-cursor/{safe_name}/project.json",
                json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
            )


def _path_size(path: Path) -> int:
    return _directory_size(path)


def _raise_if_cancelled(cancel: Callable[[], bool]) -> None:
    if cancel():
        raise DownloadCancelledError


def _safe_arc_name(project_root: Path, index: int) -> str:
    stem = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in project_root.name).strip("_")
    if not stem:
        stem = "project"
    return f"{index:02d}_{stem[:48]}"


def _write_file(archive: zipfile.ZipFile, source: Path, arcname: str, state: _PackState) -> None:
    try:
        size = source.stat().st_size
    except OSError as exc:
        state.skipped.append(f"{source} ({exc})")
        return
    try:
        # Large chat DBs need Zip64; archive.write enables it when needed.
        archive.write(source, arcname, compress_type=_compress_type(source))
    except OSError as exc:
        state.skipped.append(f"{source} ({exc})")
        return
    state.file_count += 1
    state.byte_count += size


PART_USER = "Cursor User (settings, chats, workspaceStorage)"
PART_DOT_CURSOR = "Home .cursor (projects, rules, skills, agent transcripts)"
PART_EXTENSIONS = "Home .cursor/extensions"
PART_PROJECT_CURSOR = "Project .cursor folders (rules from workspaces)"

PART_LABELS: dict[BackupPart, str] = {
    BackupPart.USER: PART_USER,
    BackupPart.DOT_CURSOR: PART_DOT_CURSOR,
    BackupPart.EXTENSIONS: PART_EXTENSIONS,
    BackupPart.PROJECT_CURSOR: PART_PROJECT_CURSOR,
}

LABEL_TO_PART: dict[str, BackupPart] = {label: part for part, label in PART_LABELS.items()}

DEFAULT_PARTS: tuple[BackupPart, ...] = (
    BackupPart.USER,
    BackupPart.DOT_CURSOR,
    BackupPart.PROJECT_CURSOR,
)
