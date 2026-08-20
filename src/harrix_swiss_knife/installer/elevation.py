"""UAC elevation helpers for the Windows installer."""

from __future__ import annotations

import ctypes
import os
import sys


def is_admin() -> bool:
    """Return whether the current process has administrator privileges."""
    if os.name != "nt":
        return True
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def relaunch_elevated(extra_args: list[str]) -> int:
    """Relaunch current process with RunAs. Returns Windows ShellExecute result (>32 = OK)."""
    if os.name != "nt":
        msg = "Elevation is Windows-only"
        raise RuntimeError(msg)
    exe = sys.executable
    # When frozen, sys.argv[0] is the exe; otherwise pass -m harrix_swiss_knife.installer
    if getattr(sys, "frozen", False):
        params = " ".join(_quote(a) for a in [*sys.argv[1:], *extra_args])
        target = exe
    else:
        params = " ".join(_quote(a) for a in ["-m", "harrix_swiss_knife.installer", *sys.argv[1:], *extra_args])
        target = exe
    return int(
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            target,
            params,
            None,
            1,
        )
    )


def _quote(arg: str) -> str:
    if not arg or any(c in arg for c in ' \t"'):
        return '"' + arg.replace('"', '\\"') + '"'
    return arg
