"""Discover and clean common temporary / reclaimable disk locations on Windows."""

from __future__ import annotations

import contextlib
import ctypes
import os
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife.paths import clear_directory_contents, clear_temp_folder, get_project_root

ProgressCallback = Callable[[str], None]

# Keep pending speech recordings when clearing `%LOCALAPPDATA%\\HarrixSwissKnife`.
_HSK_LOCAL_KEEP_NAMES = frozenset({"speech_to_text"})

_SHERB_NOCONFIRMATION = 0x00000001
_SHERB_NOPROGRESSUI = 0x00000002
_SHERB_NOSOUND = 0x00000004


@dataclass(frozen=True)
class CleanupRunResult:
    """Outcome of cleaning selected targets."""

    expected_bytes: int
    lines: tuple[str, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class CleanupTarget:
    """One reclaimable location offered in the cleanup dialog."""

    id: str
    title: str
    path_display: str
    size_bytes: int
    default_selected: bool
    cleaner: Callable[[], list[str]]

    def choice_label(self) -> str:
        """Return checkbox label with size, title, and path."""
        size = h.file.format_byte_size(self.size_bytes)
        return f"[{size}] {self.title} — {self.path_display}"


@dataclass(frozen=True)
class _CandidateSpec:
    """Internal candidate before size filtering."""

    id: str
    title: str
    path_display: str
    default_selected: bool
    size_fn: Callable[[], int]
    cleaner: Callable[[], list[str]]


class _SHQUERYRBINFO(ctypes.Structure):
    """Shell recycle-bin query structure (`SHQUERYRBINFO`)."""

    _fields_ = (
        ("cbSize", ctypes.c_ulong),
        ("i64Size", ctypes.c_int64),
        ("i64NumItems", ctypes.c_int64),
    )


def discover_targets(
    *,
    on_progress: ProgressCallback | None = None,
    on_found: Callable[[CleanupTarget], None] | None = None,
) -> list[CleanupTarget]:
    """Scan known cleanup locations; return only those with size greater than zero.

    Args:

    - `on_progress` (`ProgressCallback | None`): Called with a log line before each measure.
    - `on_found` (`Callable[[CleanupTarget], None] | None`): Called when a non-empty
      target is discovered (for live totals while scanning).

    """
    specs = _candidate_specs()
    found: list[CleanupTarget] = []
    for spec in specs:
        if on_progress is not None:
            on_progress(f"🔵 Measuring: {spec.title}")
        size = spec.size_fn()
        if size <= 0:
            continue
        target = CleanupTarget(
            id=spec.id,
            title=spec.title,
            path_display=spec.path_display,
            size_bytes=size,
            default_selected=spec.default_selected,
            cleaner=spec.cleaner,
        )
        found.append(target)
        if on_found is not None:
            on_found(target)
    return found


def folder_size(path: Path) -> int:
    """Return total size of `path` (file or directory); skip inaccessible entries."""
    if not path.exists():
        return 0
    if path.is_file():
        with contextlib.suppress(OSError):
            return path.stat().st_size
        return 0

    total = 0
    for root, _dirs, files in os.walk(path, onerror=lambda _exc: None):
        for name in files:
            file_path = Path(root) / name
            with contextlib.suppress(OSError):
                total += file_path.stat().st_size
    return total


def format_cleanup_choice_sizes(targets: list[CleanupTarget]) -> dict[str, int]:
    """Map checkbox labels to byte sizes for the selection dialog footer."""
    return {target.choice_label(): target.size_bytes for target in targets}


def paths_size(paths: list[Path]) -> int:
    """Sum sizes of existing paths (files or folders)."""
    return sum(folder_size(path) for path in paths)


def run_cleanup(targets: list[CleanupTarget], *, on_progress: ProgressCallback | None = None) -> CleanupRunResult:
    """Run cleaners for selected targets; collect log lines and errors."""
    lines: list[str] = []
    errors: list[str] = []
    expected = sum(target.size_bytes for target in targets)

    for target in targets:
        if on_progress is not None:
            on_progress(f"🔵 Cleaning: {target.title}")
        lines.append(f"Cleaning `{target.title}` ({h.file.format_byte_size(target.size_bytes)})…")
        try:
            cleaner_lines = target.cleaner()
            lines.extend(cleaner_lines)
            lines.append(f"✅ Cleaned `{target.title}`.")
        except OSError as exc:
            message = f"❌ Failed `{target.title}`: {exc}"
            lines.append(message)
            errors.append(message)

    return CleanupRunResult(expected_bytes=expected, lines=tuple(lines), errors=tuple(errors))


def _candidate_specs() -> list[_CandidateSpec]:
    """Build the ordered list of cleanup candidate definitions."""
    project_temp = get_project_root() / "temp"
    user_temp = _user_temp_path()
    system_root = Path(os.environ.get("SYSTEMROOT", r"C:\Windows"))
    windows_temp = system_root / "Temp"
    windows_old = Path(os.environ.get("SYSTEMDRIVE", "C:")) / "Windows.old"
    hsk_local = _hsk_local_appdata_dir()
    hsk_setup = Path(r"C:\hsk-setup")
    crash_dumps = _local_appdata() / "CrashDumps"
    explorer_dir = _local_appdata() / "Microsoft" / "Windows" / "Explorer"
    do_cache = system_root / "SoftwareDistribution" / "DeliveryOptimization" / "Cache"
    wu_download = system_root / "SoftwareDistribution" / "Download"
    edge_cache = _local_appdata() / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache"
    chrome_cache = _local_appdata() / "Google" / "Chrome" / "User Data" / "Default" / "Cache"

    return [
        _CandidateSpec(
            id="project_temp",
            title="Project temp (HSK)",
            path_display=str(project_temp),
            default_selected=True,
            size_fn=lambda: folder_size(project_temp),
            cleaner=lambda: clear_temp_folder(project_temp),
        ),
        _CandidateSpec(
            id="user_temp",
            title="User Temp",
            path_display=str(user_temp),
            default_selected=True,
            size_fn=lambda: folder_size(user_temp),
            cleaner=lambda: _clear_directory_report(user_temp),
        ),
        _CandidateSpec(
            id="windows_temp",
            title="Windows Temp",
            path_display=str(windows_temp),
            default_selected=False,
            size_fn=lambda: folder_size(windows_temp),
            cleaner=lambda: _clear_directory_report(windows_temp),
        ),
        _CandidateSpec(
            id="recycle_bin",
            title="Recycle Bin",
            path_display="Recycle Bin",
            default_selected=True,
            size_fn=_recycle_bin_size,
            cleaner=_empty_recycle_bin,
        ),
        _CandidateSpec(
            id="windows_old",
            title="Windows.old",
            path_display=str(windows_old),
            default_selected=False,
            size_fn=lambda: folder_size(windows_old),
            cleaner=lambda: _remove_tree_report(windows_old),
        ),
        _CandidateSpec(
            id="hsk_localappdata",
            title="HSK LocalAppData cache",
            path_display=str(hsk_local),
            default_selected=True,
            size_fn=lambda: _hsk_local_reclaimable_size(hsk_local),
            cleaner=lambda: _clear_hsk_local(hsk_local),
        ),
        _CandidateSpec(
            id="hsk_setup",
            title="HSK setup leftovers",
            path_display=str(hsk_setup),
            default_selected=True,
            size_fn=lambda: folder_size(hsk_setup),
            cleaner=lambda: _remove_tree_report(hsk_setup),
        ),
        _CandidateSpec(
            id="thumbnails",
            title="Thumbnail cache",
            path_display=str(explorer_dir / "thumbcache_*.db"),
            default_selected=False,
            size_fn=lambda: paths_size(_thumbnail_cache_files(explorer_dir)),
            cleaner=lambda: _delete_files_report(_thumbnail_cache_files(explorer_dir)),
        ),
        _CandidateSpec(
            id="do_cache",
            title="Delivery Optimization cache",
            path_display=str(do_cache),
            default_selected=False,
            size_fn=lambda: folder_size(do_cache),
            cleaner=lambda: _clear_directory_report(do_cache),
        ),
        _CandidateSpec(
            id="wu_download",
            title="Windows Update download cache",
            path_display=str(wu_download),
            default_selected=False,
            size_fn=lambda: folder_size(wu_download),
            cleaner=lambda: _clear_directory_report(wu_download),
        ),
        _CandidateSpec(
            id="crash_dumps",
            title="Crash dumps",
            path_display=str(crash_dumps),
            default_selected=True,
            size_fn=lambda: folder_size(crash_dumps),
            cleaner=lambda: _clear_directory_report(crash_dumps),
        ),
        _CandidateSpec(
            id="edge_cache",
            title="Microsoft Edge cache",
            path_display=str(edge_cache),
            default_selected=False,
            size_fn=lambda: folder_size(edge_cache),
            cleaner=lambda: _clear_directory_report(edge_cache),
        ),
        _CandidateSpec(
            id="chrome_cache",
            title="Google Chrome cache",
            path_display=str(chrome_cache),
            default_selected=False,
            size_fn=lambda: folder_size(chrome_cache),
            cleaner=lambda: _clear_directory_report(chrome_cache),
        ),
    ]


def _clear_directory_report(directory: Path) -> list[str]:
    if not directory.is_dir():
        return [f"Folder `{directory}` does not exist."]
    clear_directory_contents(directory)
    return [f"Cleared contents of `{directory}`."]


def _clear_hsk_local(root: Path) -> list[str]:
    if not root.is_dir():
        return [f"Folder `{root}` does not exist."]
    clear_directory_contents(root, keep_names=_HSK_LOCAL_KEEP_NAMES)
    return [f"Cleared `{root}` (kept: {', '.join(sorted(_HSK_LOCAL_KEEP_NAMES))})."]


def _delete_files_report(paths: list[Path]) -> list[str]:
    lines: list[str] = []
    for path in paths:
        try:
            path.unlink(missing_ok=True)
            lines.append(f"Removed `{path}`.")
        except OSError as exc:
            lines.append(f"❌ Could not remove `{path}`: {exc}")
    if not lines:
        lines.append("No thumbnail cache files found.")
    return lines


def _empty_recycle_bin() -> list[str]:
    if os.name != "nt":
        return ["Recycle Bin cleanup is only supported on Windows."]
    shell32 = ctypes.windll.shell32
    flags = _SHERB_NOCONFIRMATION | _SHERB_NOPROGRESSUI | _SHERB_NOSOUND
    result = int(shell32.SHEmptyRecycleBinW(None, None, flags)) & 0xFFFFFFFF
    # S_OK (0) and ERROR_FILE_NOT_FOUND (empty bin) are success.
    if result not in {0, 0x80070002}:
        msg = f"SHEmptyRecycleBinW failed with code 0x{result:08X}"
        raise OSError(msg)
    return ["Emptied Recycle Bin."]


def _hsk_local_appdata_dir() -> Path:
    return _local_appdata() / "HarrixSwissKnife"


def _hsk_local_reclaimable_size(root: Path) -> int:
    if not root.is_dir():
        return 0
    total = 0
    for child in root.iterdir():
        if child.name in _HSK_LOCAL_KEEP_NAMES:
            continue
        total += folder_size(child)
    return total


def _local_appdata() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local)
    return Path.home() / "AppData" / "Local"


def _recycle_bin_size() -> int:
    if os.name != "nt":
        return 0
    info = _SHQUERYRBINFO()
    info.cbSize = ctypes.sizeof(_SHQUERYRBINFO)
    shell32 = ctypes.windll.shell32
    result = shell32.SHQueryRecycleBinW(None, ctypes.byref(info))
    if result != 0:
        return 0
    return max(int(info.i64Size), 0)


def _remove_tree_report(path: Path) -> list[str]:
    if not path.exists():
        return [f"`{path}` does not exist."]
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=False)
        return [f"Removed folder `{path}`."]
    path.unlink()
    return [f"Removed file `{path}`."]


def _thumbnail_cache_files(explorer_dir: Path) -> list[Path]:
    if not explorer_dir.is_dir():
        return []
    return sorted(explorer_dir.glob("thumbcache_*.db"))


def _user_temp_path() -> Path:
    temp = os.environ.get("TEMP") or os.environ.get("TMP")
    if temp:
        return Path(temp)
    return _local_appdata() / "Temp"
