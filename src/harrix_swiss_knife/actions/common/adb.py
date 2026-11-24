"""Shared helpers for resolving and talking to `adb` devices."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife.actions.common.android_gradle import resolve_android_home
from harrix_swiss_knife.actions.common.subprocess_run import hidden_subprocess_kwargs

_MIN_DEVICE_COLUMNS = 2
_ADB_TIMEOUT_SEC = 120.0


def adb_pull(adb: Path, serial: str, remote_path: str, local_path: Path) -> subprocess.CompletedProcess[str]:
    """Pull a remote file onto the PC with ``adb -s SERIAL pull``."""
    local_path.parent.mkdir(parents=True, exist_ok=True)
    return _run_adb(
        adb,
        ["-s", serial, "pull", remote_path, str(local_path)],
    )


def adb_push(adb: Path, serial: str, local_path: Path, remote_path: str) -> subprocess.CompletedProcess[str]:
    """Push a local file to the device with ``adb -s SERIAL push``."""
    return _run_adb(
        adb,
        ["-s", serial, "push", str(local_path), remote_path],
    )


def adb_shell_getprop(adb: Path, serial: str, prop: str) -> str | None:
    """Return a trimmed ``getprop`` value from a device, or ``None``."""
    process = _run_adb(adb, ["-s", serial, "shell", "getprop", prop])
    if process.returncode != 0:
        return None
    value = (process.stdout or "").strip()
    return value or None


def list_adb_device_states(adb: Path) -> tuple[list[str], list[str], str]:
    """Return `(authorized, unauthorized, combined_output)` from `adb devices`.

    `combined_output` is non-empty when the command fails or prints diagnostics.

    """
    process = _run_adb(adb, ["devices"])
    combined = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
    if process.returncode != 0:
        return [], [], combined

    authorized: list[str] = []
    unauthorized: list[str] = []
    for raw_line in (process.stdout or "").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("List of devices"):
            continue
        parts = stripped.split()
        if len(parts) < _MIN_DEVICE_COLUMNS:
            continue
        serial, state = parts[0], parts[1]
        if state == "device":
            authorized.append(serial)
        elif state == "unauthorized":
            unauthorized.append(serial)
    return authorized, unauthorized, ""


def resolve_adb() -> Path | None:
    """Resolve ``adb`` / ``adb.exe`` from Android SDK or ``PATH``."""
    android_home = resolve_android_home()
    if android_home:
        exe_name = "adb.exe" if sys.platform == "win32" else "adb"
        candidate = Path(android_home) / "platform-tools" / exe_name
        if candidate.is_file():
            return candidate

    which_cmd = "where adb" if sys.platform == "win32" else "which adb"
    which = h.dev.run_command(which_cmd, is_shell=True)
    for line in (which or "").splitlines():
        path = Path(line.strip().strip('"'))
        if path.is_file():
            return path
    return None


def _run_adb(adb: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run ``adb`` with hidden console and a default timeout."""
    return subprocess.run(
        [str(adb), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=_ADB_TIMEOUT_SEC,
        **hidden_subprocess_kwargs(),
    )
