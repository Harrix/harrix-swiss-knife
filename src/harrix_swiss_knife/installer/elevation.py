"""UAC elevation helpers for the Windows installer."""

from __future__ import annotations

import ctypes
import json
import os
import sys
import tempfile
from pathlib import Path


def is_admin() -> bool:
    """Return whether the current process has administrator privileges."""
    if os.name != "nt":
        return True
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def read_plan_file(path: Path) -> dict:
    """Load an elevated-install continuation plan from JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


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


def write_plan_file(plan_dict: dict) -> Path:
    """Write an elevated-install continuation plan to a temp JSON file."""
    path = Path(tempfile.gettempdir()) / f"hsk-install-plan-{os.getpid()}.json"
    path.write_text(json.dumps(plan_dict, indent=2), encoding="utf-8")
    return path


def _quote(arg: str) -> str:
    if not arg or any(c in arg for c in ' \t"'):
        return '"' + arg.replace('"', '\\"') + '"'
    return arg
