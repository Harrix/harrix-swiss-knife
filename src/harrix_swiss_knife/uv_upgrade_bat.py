"""Build a detached Windows .cmd that upgrades uv packages after HSK exits."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

PROJECT_NAMES: tuple[str, ...] = ("harrix-swiss-knife", "harrix-pylib", "harrix-pyssg")
WAIT_TIMEOUT_SECONDS = 120
_LOG_NAME = "hsk-uv-upgrade.log"


def build_relaunch_command(argv: Sequence[str]) -> str:
    """Return a space-joined cmd line for restarting with the same argv."""
    return " ".join(quote_cmd_arg(part) for part in argv)


def build_uv_upgrade_cmd(
    *,
    wait_pid: int,
    uv_exe: Path,
    project_dirs: Sequence[Path],
    relaunch_argv: Sequence[str],
    log_path: Path | None = None,
    wait_timeout_seconds: int = WAIT_TIMEOUT_SECONDS,
) -> str:
    """Return the text of a `.cmd` that waits for HSK, upgrades, then relaunches.

    On failure the script still relaunches after `pause` so the user is not left
    without the app. Progress is echoed and appended to `log_path`.

    """
    uv = str(uv_exe)
    log = str(log_path) if log_path is not None else str(Path(os.environ.get("TEMP", ".")) / _LOG_NAME)
    relaunch = build_relaunch_command(relaunch_argv)
    lines: list[str] = [
        "@echo off",
        "setlocal EnableExtensions",
        f'set "UV={uv}"',
        f'set "LOG={log}"',
        f"set WAIT_PID={wait_pid}",
        f"set WAIT_MAX={wait_timeout_seconds}",
        'echo HSK uv package upgrade > "%LOG%"',
        "echo Waiting for process %WAIT_PID% to exit...",
        'echo Waiting for process %WAIT_PID% to exit...>> "%LOG%"',
        "set /a waited=0",
        ":wait_loop",
        'tasklist /FI "PID eq %WAIT_PID%" 2>nul | find "%WAIT_PID%" >nul',
        "if errorlevel 1 goto wait_done",
        "if %waited% geq %WAIT_MAX% (",
        '  echo Timed out waiting for PID %WAIT_PID%.>> "%LOG%"',
        "  echo Timed out waiting for PID %WAIT_PID%. Continuing anyway.",
        "  goto wait_done",
        ")",
        "timeout /t 1 /nobreak >nul",
        "set /a waited+=1",
        "goto wait_loop",
        ":wait_done",
        "echo.",
        "echo === uv self update ===",
        'echo === uv self update ===>> "%LOG%"',
        '"%UV%" self update',
        "if errorlevel 1 (",
        '  echo uv self update failed.>> "%LOG%"',
        "  goto fail",
        ")",
    ]
    for project in project_dirs:
        root = str(project)
        lines.extend(
            [
                "echo.",
                f"echo === {project.name}: uv python upgrade ===",
                f'echo === {project.name}: uv python upgrade ===>> "%LOG%"',
                f"cd /d {quote_cmd_arg(root)}",
                "if errorlevel 1 (",
                f'  echo cd failed for {project.name}.>> "%LOG%"',
                "  goto fail",
                ")",
                '"%UV%" python upgrade',
                "if errorlevel 1 (",
                f'  echo uv python upgrade failed in {project.name}.>> "%LOG%"',
                "  goto fail",
                ")",
                f"echo === {project.name}: uv sync --upgrade ===",
                f'echo === {project.name}: uv sync --upgrade ===>> "%LOG%"',
                '"%UV%" sync --upgrade',
                "if errorlevel 1 (",
                f'  echo uv sync --upgrade failed in {project.name}.>> "%LOG%"',
                "  goto fail",
                ")",
            ]
        )
    lines.extend(
        [
            "echo.",
            "echo === Upgrade finished ===",
            'echo === Upgrade finished ===>> "%LOG%"',
            "goto relaunch",
            ":fail",
            "echo.",
            "echo Upgrade failed. See log: %LOG%",
            'echo Upgrade failed. See log: %LOG%>> "%LOG%"',
            "pause",
            ":relaunch",
            "echo Relaunching Harrix Swiss Knife...",
            'echo Relaunching Harrix Swiss Knife...>> "%LOG%"',
            f'start "" {relaunch}',
            "endlocal",
            "exit /b 0",
            "",
        ]
    )
    return "\r\n".join(lines)


def quote_cmd_arg(value: str) -> str:
    """Quote a single argument for `cmd.exe` / `CreateProcess` style parsing."""
    if not value:
        return '""'
    if re.search(r'[\s"&<>|^]', value) is None:
        return value
    escaped = value.replace('"', '""')
    return f'"{escaped}"'


def resolve_upgrade_projects(paths_python_projects: Sequence[object]) -> list[Path]:
    """Return existing dirs for the three Harrix projects from config paths.

    Args:

    - `paths_python_projects` (`Sequence[object]`): Entries from `config.json`.

    Returns:

    - `list[Path]`: Resolved project roots in `PROJECT_NAMES` order (missing skipped).

    """
    by_name: dict[str, Path] = {}
    for entry in paths_python_projects:
        path = Path(str(entry)).expanduser()
        name = path.name
        if name not in PROJECT_NAMES or name in by_name:
            continue
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved.is_dir():
            by_name[name] = resolved
    return [by_name[name] for name in PROJECT_NAMES if name in by_name]


def write_uv_upgrade_cmd(
    path: Path,
    *,
    wait_pid: int,
    uv_exe: Path,
    project_dirs: Sequence[Path],
    relaunch_argv: Sequence[str],
    log_path: Path | None = None,
    wait_timeout_seconds: int = WAIT_TIMEOUT_SECONDS,
) -> Path:
    """Write the upgrade `.cmd` to `path` and return `path`."""
    text = build_uv_upgrade_cmd(
        wait_pid=wait_pid,
        uv_exe=uv_exe,
        project_dirs=project_dirs,
        relaunch_argv=relaunch_argv,
        log_path=log_path,
        wait_timeout_seconds=wait_timeout_seconds,
    )
    path.write_text(text, encoding="utf-8", newline="")
    return path
