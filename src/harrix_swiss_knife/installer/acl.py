"""Grant the installing Windows user write access after an elevated install."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from harrix_swiss_knife.installer.log import OutcomeLog


def installing_username() -> str:
    """Return the Windows user who launched the elevated installer."""
    for key in ("USERNAME", "USER"):
        value = (os.environ.get(key) or "").strip()
        if value:
            return value
    return ""


def repair_install_tree_acls(target: Path, log: OutcomeLog) -> bool:
    """Clear read-only, grant Full Control to the installing user, set Medium integrity.

    Returns whether every step that was attempted succeeded. Missing tools are logged
    and treated as failure without raising.

    """
    if sys.platform != "win32":
        log.add("skipped", "ACL repair skipped (not Windows)")
        return True
    if not target.exists():
        log.add("failed", f"ACL repair skipped: path missing ({target})")
        return False

    user = installing_username()
    if not user:
        log.add("failed", "ACL repair skipped: USERNAME not set")
        return False

    log.step("Repair folder permissions for the current user")
    log.detail(f"Target: {target}")
    log.detail(f"User: {user}")

    ok = True
    if not _run_cmd(["attrib", "-R", str(target), "/S", "/D"], log, label="attrib -R"):
        ok = False
    grant = ["icacls", str(target), "/grant", f"{user}:(OI)(CI)F", "/T", "/C", "/Q"]
    if not _run_cmd(grant, log, label="icacls /grant"):
        ok = False
    integrity = ["icacls", str(target), "/setintegritylevel", "(OI)(CI)M", "/T", "/C", "/Q"]
    if not _run_cmd(integrity, log, label="icacls /setintegritylevel"):
        # Integrity can fail on some volumes; keep grant result as the main signal.
        log.detail("Medium integrity level could not be set (continuing)")

    if ok:
        log.add("installed", f"Granted Full Control on {target} to {user}")
    else:
        log.add("failed", f"ACL repair incomplete for {target}")
    return ok


def _run_cmd(cmd: list[str], log: OutcomeLog, *, label: str) -> bool:
    creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation,
        )
    except FileNotFoundError:
        log.detail(f"{label}: command not found ({cmd[0]})")
        return False
    except OSError as exc:
        log.detail(f"{label}: {exc}")
        return False
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()[:500]
        log.detail(f"{label} exit {proc.returncode}" + (f": {err}" if err else ""))
        return False
    return True
