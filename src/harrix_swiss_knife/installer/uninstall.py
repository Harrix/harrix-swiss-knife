"""Uninstall Harrix Swiss Knife while preserving user databases and secrets."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from harrix_swiss_knife.desktop_shortcut import remove_app_shortcuts
from harrix_swiss_knife.installer.arp import unregister_uninstall
from harrix_swiss_knife.installer.constants import HSK_REPO_NAME, REPO_NAMES
from harrix_swiss_knife.installer.prereqs import find_uv_exe

if TYPE_CHECKING:
    from harrix_swiss_knife.installer.log import OutcomeLog

_DB_CONFIG_KEYS = (
    "sqlite_finance",
    "sqlite_fitness",
    "sqlite_habits",
    "sqlite_food",
    "sqlite_snippets",
)
_PRESERVE_DIR_NAME = "Harrix Swiss Knife Data"
_SQLITE_SUFFIX = ".db"
_REPO_ROOT_PARENT_DEPTH = 4
_DELETE_ATTEMPTS = 3


@dataclass
class UninstallOptions:
    """User choices for an uninstall run."""

    hsk_path: Path
    remove_sibling_repos: bool = True


@dataclass
class UninstallResult:
    """Outcome of `run_uninstall`."""

    ok: bool
    hsk_path: Path | None
    preserved_dir: Path | None
    outcomes: OutcomeLog
    error: str | None = None
    elapsed_seconds: float = 0.0
    preserved_items: list[str] = field(default_factory=list)


def default_preserve_dir(hsk_path: Path) -> Path:
    """Return the folder where databases and secrets are moved before deletion."""
    parent = hsk_path.parent
    docs = Path.home() / "Documents" / _PRESERVE_DIR_NAME
    try:
        parent.mkdir(parents=True, exist_ok=True)
        probe = parent / ".hsk-uninstall-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError:
        return docs
    return parent / _PRESERVE_DIR_NAME


def detect_hsk_path(hint: Path | None = None) -> Path | None:
    """Locate an installed `harrix-swiss-knife` checkout."""
    candidates: list[Path] = []
    if hint is not None:
        candidates.append(hint)
    here = Path(__file__).resolve()
    # installer -> harrix_swiss_knife -> src -> repo root
    if len(here.parents) >= _REPO_ROOT_PARENT_DEPTH:
        candidates.append(here.parents[3])
    cwd = Path.cwd()
    candidates.extend((cwd, cwd / HSK_REPO_NAME, cwd.parent / HSK_REPO_NAME))
    for root in candidates:
        if _looks_like_hsk(root):
            return root.resolve()
    return None


def list_paths_to_preserve(hsk_path: Path) -> list[Path]:
    """Return files/dirs under `hsk_path` that must survive uninstall."""
    root = hsk_path.resolve()
    found: list[Path] = []
    seen: set[str] = set()

    def _add(path: Path) -> None:
        try:
            resolved = path.resolve()
        except OSError:
            return
        key = str(resolved).lower()
        if key in seen:
            return
        if not resolved.exists():
            return
        try:
            resolved.relative_to(root)
        except ValueError:
            # Outside the project tree — leave in place, do not move.
            return
        seen.add(key)
        found.append(resolved)

    config_path = root / "config" / "config.json"
    data = _read_config(config_path)
    for key in _DB_CONFIG_KEYS:
        raw = data.get(key) if data else None
        if isinstance(raw, str) and raw.strip():
            _add(Path(raw))
            if key == "sqlite_fitness":
                _add(Path(raw).parent / "fitness_img")

    db_dir = root / "data" / "databases"
    if db_dir.is_dir():
        for path in db_dir.iterdir():
            if path.is_file() and path.suffix.lower() == _SQLITE_SUFFIX:
                _add(path)
        fitness_img = db_dir / "fitness_img"
        _add(fitness_img)

    _add(root / "api-keys")
    if config_path.is_file():
        _add(config_path)
    return found


def preserve_user_data(hsk_path: Path, dest: Path, log: OutcomeLog) -> list[str]:
    """Move databases, API keys, and fitness images out of the project tree."""
    items = list_paths_to_preserve(hsk_path)
    if not items:
        log.add("already", "No databases or api-keys found under the project to preserve")
        return []
    dest.mkdir(parents=True, exist_ok=True)
    preserved: list[str] = []
    root = hsk_path.resolve()
    for src in items:
        rel = src.relative_to(root)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            stamp = time.strftime("%Y%m%d-%H%M%S")
            target = target.with_name(f"{target.stem}-kept-{stamp}{target.suffix}")
        log.detail(f"Preserving {rel} -> {target}")
        shutil.move(str(src), str(target))
        preserved.append(str(target))
    readme = dest / "README.txt"
    readme.write_text(
        "Harrix Swiss Knife — preserved user data after uninstall.\n"
        "\n"
        "Databases, api-keys, and fitness images were moved here so the app folders\n"
        "could be removed. Reinstall and point config.json sqlite_* paths here, or\n"
        "copy files back into the new install's data/databases and api-keys folders.\n",
        encoding="utf-8",
    )
    log.add("installed", f"Preserved user data in {dest}")
    return preserved


def run_uninstall(options: UninstallOptions, log: OutcomeLog) -> UninstallResult:
    """Remove the app install; keep databases and related user data."""
    started = time.perf_counter()
    hsk = options.hsk_path.resolve()
    if not _looks_like_hsk(hsk):
        return UninstallResult(
            ok=False,
            hsk_path=hsk,
            preserved_dir=None,
            outcomes=log,
            error=f"Not a Harrix Swiss Knife install: {hsk}",
            elapsed_seconds=time.perf_counter() - started,
        )

    try:
        log.step("Uninstall Harrix Swiss Knife")
        log.detail(f"Project: {hsk}")
        log.detail("Databases, api-keys, and fitness images are kept; Git/uv/VS Code/Python stay installed.")

        _stop_running_app(hsk, log)

        preserve_dir = default_preserve_dir(hsk)
        preserved = preserve_user_data(hsk, preserve_dir, log)

        log.step("Remove shortcuts")
        try:
            removed = remove_app_shortcuts()
            if removed:
                for path in removed:
                    log.add("installed", f"Removed shortcut {path}")
            else:
                log.add("already", "No desktop/startup/uninstall shortcuts found")
        except OSError as exc:
            log.add("failed", f"Shortcut removal failed: {exc}")

        log.step("Remove global hsk CLI (uv tool)")
        _uninstall_cli(log)

        log.step("Remove Apps & Features entry")
        unregister_uninstall(log)

        install_root = hsk.parent
        to_remove = [hsk]
        if options.remove_sibling_repos:
            for name in REPO_NAMES:
                if name == HSK_REPO_NAME:
                    continue
                sibling = install_root / name
                if sibling.is_dir():
                    to_remove.append(sibling.resolve())

        log.step("Remove install folders")
        for path in to_remove:
            log.detail(f"Deleting {path}")
            _rmtree_retry(path, log)
            if path.exists():
                log.add("failed", f"Could not fully delete {path}")
            else:
                log.add("installed", f"Removed {path.name}")

        log.step("Done")
        log.line("")
        log.line(f"Preserved data:  {preserve_dir if preserved else '(nothing under project)'}")
        for line in log.summary_lines(action_label="What was removed:"):
            log.line(line)
        return UninstallResult(
            ok=True,
            hsk_path=hsk,
            preserved_dir=preserve_dir if preserved else None,
            outcomes=log,
            elapsed_seconds=time.perf_counter() - started,
            preserved_items=preserved,
        )
    except Exception as exc:
        log.line(f"❌ ERROR: {exc}")
        return UninstallResult(
            ok=False,
            hsk_path=hsk,
            preserved_dir=None,
            outcomes=log,
            error=str(exc),
            elapsed_seconds=time.perf_counter() - started,
        )


def _looks_like_hsk(path: Path) -> bool:
    if not path.is_dir():
        return False
    if path.name.lower() != HSK_REPO_NAME.lower():
        return False
    pyproject = path / "pyproject.toml"
    if not pyproject.is_file():
        return False
    text = pyproject.read_text(encoding="utf-8", errors="replace")[:2000]
    return 'name = "harrix-swiss-knife"' in text or "name='harrix-swiss-knife'" in text


def _read_config(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _rmtree_retry(path: Path, log: OutcomeLog) -> None:
    if not path.exists():
        return
    for attempt in range(_DELETE_ATTEMPTS):
        try:
            shutil.rmtree(path)
        except OSError as exc:
            log.detail(f"Delete retry {attempt + 1}/{_DELETE_ATTEMPTS} for {path}: {exc}")
            time.sleep(0.4)
        else:
            return
    # Last attempt: ignore errors so remaining locked files do not abort the rest.
    shutil.rmtree(path, ignore_errors=True)


def _stop_running_app(hsk_path: Path, log: OutcomeLog) -> None:
    if sys.platform != "win32":
        return
    creation = subprocess.CREATE_NO_WINDOW
    # Narrow match: only processes whose command line mentions this install path.
    needle = str(hsk_path).replace("'", "''")
    script = (
        "$needle = '" + needle + "'.ToLowerInvariant(); "
        "Get-CimInstance Win32_Process | "
        "Where-Object { "
        "  $_.Name -match '^(python|pythonw|harrix-swiss-knife)\\.exe$' -and "
        "  $_.CommandLine -and $_.CommandLine.ToLowerInvariant().Contains($needle) "
        "} | ForEach-Object { "
        "  Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue "
        "}"
    )
    try:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            log.detail("Could not stop running app processes: powershell not found")
            return
        proc = subprocess.run(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation,
        )
    except OSError as exc:
        log.detail(f"Could not stop running app processes: {exc}")
        return
    if proc.returncode == 0:
        log.detail("Stopped running Harrix Swiss Knife processes (if any)")
    else:
        log.detail("No running app processes found (or stop skipped)")


def _uninstall_cli(log: OutcomeLog) -> None:
    uv = find_uv_exe()
    if uv is None:
        log.add("skipped", "CLI not removed (uv missing)")
        return
    creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    proc = subprocess.run(
        [str(uv), "tool", "uninstall", "harrix-swiss-knife"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creation,
    )
    if proc.stdout.strip():
        log.detail(proc.stdout.strip()[:1500])
    if proc.stderr.strip():
        log.detail(proc.stderr.strip()[:1500])
    if proc.returncode == 0:
        log.add("installed", "Removed global CLI (uv tool uninstall harrix-swiss-knife)")
        return
    # Older uv / already gone
    log.add("skipped", "CLI not removed via uv tool uninstall (may already be absent)")
    local_bin = Path.home() / ".local" / "bin"
    for name in ("hsk.exe", "hsk", "harrix-swiss-knife.exe", "harrix-swiss-knife"):
        shim = local_bin / name
        if shim.is_file():
            try:
                shim.unlink()
                log.add("installed", f"Removed leftover shim {shim}")
            except OSError as exc:
                log.add("failed", f"Could not remove {shim}: {exc}")


# Re-export for callers / tests
__all__ = [
    "UninstallOptions",
    "UninstallResult",
    "default_preserve_dir",
    "detect_hsk_path",
    "list_paths_to_preserve",
    "preserve_user_data",
    "run_uninstall",
]
