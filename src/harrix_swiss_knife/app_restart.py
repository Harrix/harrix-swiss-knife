"""Restart the running Harrix Swiss Knife process."""

from __future__ import annotations

import subprocess
import sys
from typing import Any

from PySide6.QtWidgets import QApplication


def restart_argv() -> list[str]:
    """Return argv that starts the same interpreter and entry script.

    Returns:

    - `list[str]`: `sys.executable` followed by `sys.argv`.

    """
    return [sys.executable, *sys.argv]


def restart_current_application() -> bool:
    """Spawn a replacement process, then quit the current Qt application.

    Returns:

    - `bool`: `True` when the new process was started.

    """
    if not spawn_replacement_process():
        return False
    app = QApplication.instance()
    if app is not None:
        app.quit()
    return True


def spawn_replacement_process(argv: list[str] | None = None) -> subprocess.Popen[str] | None:
    """Start a detached copy of this process.

    Args:

    - `argv` (`list[str] | None`): Command to start. Defaults to `restart_argv()`.

    Returns:

    - `subprocess.Popen[str] | None`: The new process, or `None` on failure.

    """
    command = list(argv) if argv is not None else restart_argv()
    if not command:
        return None
    kwargs: dict[str, Any] = {"close_fds": True}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    try:
        return subprocess.Popen(command, **kwargs)
    except OSError:
        return None
