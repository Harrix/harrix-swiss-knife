"""Clone or extract sibling repositories."""

from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from typing import TYPE_CHECKING

from harrix_swiss_knife.installer.constants import REPO_NAMES

if TYPE_CHECKING:
    from pathlib import Path

    from harrix_swiss_knife.installer.log import OutcomeLog

_REPO_URLS = {
    "harrix-pylib": "https://github.com/Harrix/harrix-pylib.git",
    "harrix-pyssg": "https://github.com/Harrix/harrix-pyssg.git",
    "harrix-swiss-knife": "https://github.com/Harrix/harrix-swiss-knife.git",
}


def ensure_repos(
    install_root: Path,
    *,
    deps: Path,
    offline: bool,
    log: OutcomeLog,
) -> Path:
    """Ensure sibling repos exist under `install_root`. Return harrix-swiss-knife path."""
    log.step("Get source repositories")
    if offline:
        log.detail("Offline EXE: extract snapshots from the bundled repos/ zip files when present")
    else:
        log.detail("Online EXE: git clone from GitHub (or git pull if the folder already exists)")
    hsk_path = install_root / "harrix-swiss-knife"
    for name in REPO_NAMES:
        path = install_root / name
        if repo_ready_or_reset(path, label=name, allow_offline=offline, log=log):
            log.detail(f"{name} already present at {path}")
            log.add("already", f"{name} already present")
            if not offline:
                log.detail(f"Updating {name} with git pull --ff-only (skipped if there are local changes)")
                update_git_repo(path, label=name, log=log)
            continue
        snap = deps / "repos" / f"{name}.zip"
        if offline and snap.is_file():
            log.detail(f"Extracting {name} from bundled snapshot {snap.name}")
            expand_repo_snapshot(snap, path)
            log.add("installed", f"Extracted {name} from offline snapshot")
            continue
        url = _REPO_URLS[name]
        log.detail(f"git clone {url}")
        code = _git(["-C", str(install_root), "clone", url], log)
        if code != 0:
            msg = f"git clone {name} failed (exit {code})"
            raise RuntimeError(msg)
        log.add("installed", f"Cloned {name} from GitHub")
    return hsk_path


def expand_repo_snapshot(zip_path: Path, destination: Path) -> None:
    """Extract a repository snapshot zip into `destination`."""
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(destination)


def repo_ready_or_reset(path: Path, *, label: str, allow_offline: bool, log: OutcomeLog) -> bool:
    """Return whether `path` is a usable repo; reset empty non-git folders."""
    if not path.exists():
        return False
    if (path / ".git").exists():
        return True
    items = list(path.iterdir()) if path.is_dir() else []
    if not items:
        log.detail(f"Removing empty non-git folder: {path}")
        path.rmdir()
        return False
    if allow_offline and (path / "pyproject.toml").is_file():
        log.detail(f"{label} present as offline snapshot (no .git); skip re-extract")
        return True
    msg = f"{label} folder exists but is not a git repository: {path}"
    raise RuntimeError(msg)


def update_git_repo(path: Path, *, label: str, log: OutcomeLog) -> None:
    """Fast-forward `path` when it is a clean Git checkout."""
    git_exe = shutil.which("git")
    if git_exe is None:
        log.add("skipped", f"{label} not updated (git not available)")
        return
    if not (path / ".git").is_dir():
        log.add("skipped", f"{label} not updated (no .git folder)")
        return
    status = subprocess.run(
        [git_exe, "-C", str(path), "status", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    if status.returncode != 0:
        log.add("skipped", f"{label} not updated (git status failed)")
        return
    if status.stdout.strip():
        log.add("skipped", f"{label} not updated (local changes present)")
        return
    if _git(["-C", str(path), "fetch", "--prune"], log) != 0:
        log.add("skipped", f"{label} not updated (git fetch failed)")
        return
    if _git(["-C", str(path), "pull", "--ff-only"], log) != 0:
        log.add("skipped", f"{label} not updated (git pull failed)")
        return
    log.add("installed", f"Updated {label} (git pull)")


def _git(args: list[str], log: OutcomeLog) -> int:
    git_exe = shutil.which("git")
    if git_exe is None:
        return 1
    creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    proc = subprocess.run(
        [git_exe, "-c", "core.longpaths=true", *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creation,
    )
    for stream in (proc.stdout, proc.stderr):
        if stream and stream.strip():
            for line in stream.strip().splitlines():
                log.detail(line)
    return int(proc.returncode)
