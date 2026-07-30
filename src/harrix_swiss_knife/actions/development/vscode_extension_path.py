"""Shared helpers for VS Code extension Biome format / check actions."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import harrix_pylib as h

EXTENSION_RELATIVE = Path("vscode") / "harrix-notes-explorer-hsk"


def ensure_node_modules(extension_dir: Path) -> subprocess.CompletedProcess[str] | None:
    """Run `npm ci` or `npm install` when `node_modules` is missing.

    Returns the completed process if install was run, or `None` if dependencies
    were already present.

    """
    if (extension_dir / "node_modules" / "@biomejs" / "biome").is_dir():
        return None

    if resolve_npm() is None:
        msg = "npm not found"
        raise FileNotFoundError(msg)

    lockfile = extension_dir / "package-lock.json"
    return run_npm(extension_dir, "ci" if lockfile.is_file() else "install")


def resolve_extension_dir() -> Path | None:
    """Return the Notes Explorer extension folder if ``package.json`` exists."""
    extension_dir = h.dev.get_project_root() / EXTENSION_RELATIVE
    if not extension_dir.is_dir():
        return None
    if not (extension_dir / "package.json").is_file():
        return None
    return extension_dir


def resolve_npm() -> str | None:
    """Return path to ``npm`` / ``npm.cmd`` on PATH, or ``None``."""
    for name in ("npm.cmd", "npm"):
        found = shutil.which(name)
        if found:
            return found
    return None


def run_npm(extension_dir: Path, *npm_args: str) -> subprocess.CompletedProcess[str]:
    """Run ``npm`` with the given args in the extension directory."""
    npm = resolve_npm()
    if npm is None:
        msg = "npm not found on PATH"
        raise FileNotFoundError(msg)

    return subprocess.run(
        [npm, *npm_args],
        cwd=str(extension_dir),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        shell=False,
    )
