"""Shared subprocess helpers with timeouts and argv lists."""

from __future__ import annotations

import pathlib  # noqa: TC003
import shutil
import subprocess
import sys
from typing import Any

DEFAULT_SUBPROCESS_TIMEOUT = 300.0
QT_OFFSCREEN_PLATFORM = "offscreen:size=1920x1080"


def hidden_subprocess_kwargs() -> dict[str, Any]:
    """Return subprocess kwargs that hide a console window on Windows.

    `CREATE_NO_WINDOW` plus `SW_HIDE` covers both `*.exe` and `*.cmd` shims
    (`uv`, `python`) so short-lived check tools do not flash a console.

    Returns:

    - `dict[str, Any]`: Extra `subprocess.run` kwargs, or `{}` on non-Windows.

    """
    if sys.platform != "win32":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return {
        "creationflags": subprocess.CREATE_NO_WINDOW,
        "startupinfo": startupinfo,
    }


def run_argv(
    command: list[str],
    *,
    cwd: str | pathlib.Path | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = DEFAULT_SUBPROCESS_TIMEOUT,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a command as an argv list with a default timeout.

    Args:

    - `command` (`list[str]`): Executable and arguments (no shell).
    - `cwd` (`str | pathlib.Path | None`): Working directory. Defaults to `None`.
    - `env` (`dict[str, str] | None`): Environment variables. Defaults to `None`.
    - `timeout` (`float | None`): Timeout in seconds. Defaults to `300.0`.
    - `check` (`bool`): Raise on non-zero exit. Defaults to `False`.

    Returns:

    - `subprocess.CompletedProcess[str]`: Completed process with text output.

    """
    if not command:
        msg = "Command list must not be empty."
        raise ValueError(msg)

    executable = shutil.which(command[0]) or command[0]
    argv = [executable, *command[1:]]
    return subprocess.run(
        argv,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
        timeout=timeout,
        shell=False,
        **hidden_subprocess_kwargs(),
    )


def run_argv_output(
    command: list[str],
    *,
    cwd: str | pathlib.Path | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = DEFAULT_SUBPROCESS_TIMEOUT,
) -> tuple[int, str]:
    """Run argv command and return `(returncode, combined_output)`.

    On timeout, returncode is `-1` and output explains the timeout.

    """
    try:
        process = run_argv(command, cwd=cwd, env=env, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        return -1, f"Command timed out after {exc.timeout} seconds: {' '.join(command)}"
    except OSError as exc:
        return -1, f"Error executing command: {exc}"

    output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
    return process.returncode, "\n".join(filter(None, output_parts))


def venv_module_argv(project_path: pathlib.Path, module: str, *module_args: str) -> list[str]:
    """Build argv for `python -m <module>` inside a project's `.venv`.

    Prefer this over `uv run`: on Windows `uv` often opens a brief console even
    when the parent process used `CREATE_NO_WINDOW`.

    Args:

    - `project_path` (`pathlib.Path`): Folder that contains `.venv`.
    - `module` (`str`): Module to run (`ruff`, `ty`, `pytest`, …).
    - `module_args` (`str`): Extra arguments after `-m <module>`.

    Returns:

    - `list[str]`: Executable argv list.

    """
    return [str(venv_python(project_path)), "-m", module, *module_args]


def venv_python(project_path: pathlib.Path) -> pathlib.Path:
    """Return the project's virtualenv Python executable.

    Args:

    - `project_path` (`pathlib.Path`): Folder that contains `.venv`.

    Returns:

    - `pathlib.Path`: `.venv/Scripts/python.exe` on Windows, `.venv/bin/python` elsewhere.

    """
    if sys.platform == "win32":
        return project_path / ".venv" / "Scripts" / "python.exe"
    return project_path / ".venv" / "bin" / "python"
