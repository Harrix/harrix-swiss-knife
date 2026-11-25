"""Pack and restore Beat Saber save files (PC folder or Quest via adb)."""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from harrix_swiss_knife.actions.common.adb import adb_pull, adb_push
from harrix_swiss_knife.beat_saber_saves.paths import pc_saves_dir, quest_remote_files_dir
from harrix_swiss_knife.beat_saber_saves.report import format_progress_report

if TYPE_CHECKING:
    from collections.abc import Callable

SAVE_FILE_NAMES: tuple[str, ...] = (
    "PlayerData.dat",
    "LocalLeaderboards.dat",
    "LocalDailyLeaderboards.dat",
    "AvatarData.dat",
    "settings.cfg",
)
REQUIRED_SAVE_NAME = "PlayerData.dat"
_MANIFEST_NAME = "manifest.json"
_PROGRESS_REPORT_NAME = "progress-report.txt"
_ZIP_MEMBER_PREFIX = "saves/"


@dataclass
class BeatSaberTransferResult:
    """Outcome of an export or import."""

    ok: bool
    mode: str
    source: str
    files: list[str] = field(default_factory=list)
    zip_path: Path | None = None
    message: str = ""
    lines: list[str] = field(default_factory=list)


def export_pc_saves(
    zip_path: Path,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BeatSaberTransferResult:
    """Copy PC LocalLow save files into a ZIP."""
    folder = pc_saves_dir()
    if not folder.is_dir():
        return BeatSaberTransferResult(
            ok=False,
            mode="export",
            source="pc",
            message=f"PC saves folder not found: `{folder}`",
        )
    collected = _collect_local_files(folder)
    if REQUIRED_SAVE_NAME not in collected:
        return BeatSaberTransferResult(
            ok=False,
            mode="export",
            source="pc",
            message=f"`{REQUIRED_SAVE_NAME}` not found in `{folder}`",
        )
    if should_cancel and should_cancel():
        return BeatSaberTransferResult(ok=False, mode="export", source="pc", message="Cancelled.")
    return _write_zip(zip_path, collected, source="pc", mode="export")


def export_quest_saves(
    adb: Path,
    serial: str,
    zip_path: Path,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BeatSaberTransferResult:
    """Pull Quest Beat Saber save files into a ZIP via adb."""
    remote_dir = quest_remote_files_dir()
    lines: list[str] = []
    with tempfile.TemporaryDirectory(prefix="hsk-beat-saber-") as tmp:
        tmp_dir = Path(tmp)
        collected: dict[str, Path] = {}
        for name in SAVE_FILE_NAMES:
            if should_cancel and should_cancel():
                return BeatSaberTransferResult(
                    ok=False,
                    mode="export",
                    source="quest",
                    message="Cancelled.",
                    lines=lines,
                )
            remote = f"{remote_dir}/{name}"
            local = tmp_dir / name
            process = adb_pull(adb, serial, remote, local)
            if process.returncode == 0 and local.is_file() and local.stat().st_size > 0:
                collected[name] = local
                lines.append(f"Pulled `{name}`")
            else:
                detail = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
                if detail:
                    lines.append(f"Skip `{name}`: {detail}")
                else:
                    lines.append(f"Skip `{name}` (not on device or inaccessible)")

        if REQUIRED_SAVE_NAME not in collected:
            hint = (
                "Could not pull `PlayerData.dat`. Confirm Beat Saber is installed, "
                "USB file access is allowed, and Android/data is readable over adb "
                f"(path `{remote_dir}`)."
            )
            return BeatSaberTransferResult(
                ok=False,
                mode="export",
                source="quest",
                message=hint,
                lines=lines,
            )
        result = _write_zip(zip_path, collected, source="quest", mode="export")
        result.lines = [*lines, *result.lines]
        return result


def import_pc_saves(
    zip_path: Path,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BeatSaberTransferResult:
    """Restore save files from a ZIP into the PC LocalLow folder."""
    extracted, err = _extract_zip_saves(zip_path)
    if err or extracted is None:
        return BeatSaberTransferResult(ok=False, mode="import", source="pc", message=err or "Invalid ZIP.")
    if REQUIRED_SAVE_NAME not in extracted:
        _cleanup_temp_map(extracted)
        return BeatSaberTransferResult(
            ok=False,
            mode="import",
            source="pc",
            message=f"ZIP is missing `{REQUIRED_SAVE_NAME}`.",
        )

    folder = pc_saves_dir()
    folder.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    lines: list[str] = []
    try:
        for name, src in extracted.items():
            if should_cancel and should_cancel():
                return BeatSaberTransferResult(
                    ok=False,
                    mode="import",
                    source="pc",
                    message="Cancelled.",
                    files=written,
                    zip_path=zip_path,
                    lines=lines,
                )
            dest = folder / name
            shutil.copy2(src, dest)
            written.append(name)
            lines.append(f"Wrote `{dest}`")
    finally:
        _cleanup_temp_map(extracted)

    return BeatSaberTransferResult(
        ok=True,
        mode="import",
        source="pc",
        files=written,
        zip_path=zip_path,
        message=f"Imported {len(written)} file(s) into `{folder}`.",
        lines=lines,
    )


def import_quest_saves(
    adb: Path,
    serial: str,
    zip_path: Path,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BeatSaberTransferResult:
    """Push save files from a ZIP onto Quest via adb."""
    extracted, err = _extract_zip_saves(zip_path)
    if err or extracted is None:
        return BeatSaberTransferResult(ok=False, mode="import", source="quest", message=err or "Invalid ZIP.")
    if REQUIRED_SAVE_NAME not in extracted:
        _cleanup_temp_map(extracted)
        return BeatSaberTransferResult(
            ok=False,
            mode="import",
            source="quest",
            message=f"ZIP is missing `{REQUIRED_SAVE_NAME}`.",
        )

    remote_dir = quest_remote_files_dir()
    written: list[str] = []
    lines: list[str] = []
    try:
        for name, src in extracted.items():
            if should_cancel and should_cancel():
                return BeatSaberTransferResult(
                    ok=False,
                    mode="import",
                    source="quest",
                    message="Cancelled.",
                    files=written,
                    zip_path=zip_path,
                    lines=lines,
                )
            remote = f"{remote_dir}/{name}"
            process = adb_push(adb, serial, src, remote)
            detail = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
            if process.returncode != 0:
                lines.append(f"❌ Failed to push `{name}`: {detail or process.returncode}")
                return BeatSaberTransferResult(
                    ok=False,
                    mode="import",
                    source="quest",
                    files=written,
                    zip_path=zip_path,
                    message=f"adb push failed for `{name}`.",
                    lines=lines,
                )
            written.append(name)
            lines.append(f"Pushed `{name}` → `{remote}`")
    finally:
        _cleanup_temp_map(extracted)

    return BeatSaberTransferResult(
        ok=True,
        mode="import",
        source="quest",
        files=written,
        zip_path=zip_path,
        message=f"Imported {len(written)} file(s) to Quest (`{remote_dir}`).",
        lines=lines,
    )


def _cleanup_temp_map(files: dict[str, Path]) -> None:
    parents: set[Path] = set()
    for path in files.values():
        parents.add(path.parent)
        if path.is_file():
            path.unlink(missing_ok=True)
    for parent in parents:
        if parent.is_dir() and parent.name.startswith("hsk-beat-saber-"):
            shutil.rmtree(parent, ignore_errors=True)


def _collect_local_files(folder: Path) -> dict[str, Path]:
    collected: dict[str, Path] = {}
    for name in SAVE_FILE_NAMES:
        path = folder / name
        if path.is_file() and path.stat().st_size > 0:
            collected[name] = path
    return collected


def _extract_zip_saves(zip_path: Path) -> tuple[dict[str, Path] | None, str]:
    if not zip_path.is_file():
        return None, f"ZIP not found: `{zip_path}`"
    tmp_root = Path(tempfile.mkdtemp(prefix="hsk-beat-saber-"))
    extracted: dict[str, Path] = {}
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = set(zf.namelist())
            for save_name in SAVE_FILE_NAMES:
                member = _member_for_save(names, save_name)
                if member is None:
                    continue
                target = tmp_root / save_name
                with zf.open(member) as src, target.open("wb") as dest:
                    shutil.copyfileobj(src, dest)
                if target.is_file() and target.stat().st_size > 0:
                    extracted[save_name] = target
    except (OSError, zipfile.BadZipFile) as exc:
        shutil.rmtree(tmp_root, ignore_errors=True)
        return None, f"Could not read ZIP: {exc}"

    if not extracted:
        shutil.rmtree(tmp_root, ignore_errors=True)
        return None, "ZIP contains no Beat Saber save files."
    return extracted, ""


def _member_for_save(names: set[str], save_name: str) -> str | None:
    candidates = (
        f"{_ZIP_MEMBER_PREFIX}{save_name}",
        save_name,
        f"./{save_name}",
    )
    for candidate in candidates:
        if candidate in names:
            return candidate
    for name in names:
        normalized = name.replace("\\", "/")
        if Path(name).name == save_name and (normalized.endswith(f"/{save_name}") or name.endswith(save_name)):
            return name
    return None


def _write_zip(
    zip_path: Path,
    files: dict[str, Path],
    *,
    source: str,
    mode: str,
) -> BeatSaberTransferResult:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "app": "beat-saber",
        "source": source,
        "files": sorted(files),
    }
    progress_report = ""
    player_data = files.get(REQUIRED_SAVE_NAME)
    if player_data is not None and mode == "export":
        progress_report = format_progress_report(player_data)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(_MANIFEST_NAME, json.dumps(manifest, indent=2) + "\n")
        if progress_report:
            zf.writestr(_PROGRESS_REPORT_NAME, progress_report + "\n")
        for name, path in files.items():
            zf.write(path, arcname=f"{_ZIP_MEMBER_PREFIX}{name}")

    lines = [f"Packed `{name}`" for name in sorted(files)]
    if progress_report:
        lines.extend(["", progress_report])
    return BeatSaberTransferResult(
        ok=True,
        mode=mode,
        source=source,
        files=sorted(files),
        zip_path=zip_path,
        message=f"Exported {len(files)} file(s) to `{zip_path}`.",
        lines=lines,
    )
