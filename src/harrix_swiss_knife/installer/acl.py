"""Grant the installing Windows user write access after an elevated install."""

from __future__ import annotations

import ctypes
import os
import re
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from harrix_swiss_knife.installer.log import OutcomeLog

_FAILED_PROCESSING_RE = re.compile(r"Failed processing\s+(\d+)\s+files", re.IGNORECASE)
_SUCCESS_PROCESSING_RE = re.compile(r"Successfully processed\s+(\d+)\s+files", re.IGNORECASE)


def installing_user_principal() -> str:
    """Return an `icacls` principal: `*S-1-…` when possible, else `USERNAME`."""
    sid = installing_user_sid()
    if sid:
        return f"*{sid}"
    return installing_username()


def installing_user_sid() -> str:
    """Return the current user SID (`S-1-…`), or empty when unavailable."""
    if sys.platform != "win32":
        return ""
    try:
        token = ctypes.c_void_p()
        if not ctypes.windll.advapi32.OpenProcessToken(  # type: ignore[attr-defined]
            ctypes.windll.kernel32.GetCurrentProcess(),  # type: ignore[attr-defined]
            _TOKEN_QUERY,
            ctypes.byref(token),
        ):
            return ""
        try:
            size = ctypes.c_ulong(0)
            ctypes.windll.advapi32.GetTokenInformation(  # type: ignore[attr-defined]
                token,
                _TOKEN_USER,
                None,
                0,
                ctypes.byref(size),
            )
            if size.value == 0:
                return ""
            buf = (ctypes.c_ubyte * size.value)()
            if not ctypes.windll.advapi32.GetTokenInformation(  # type: ignore[attr-defined]
                token,
                _TOKEN_USER,
                buf,
                size,
                ctypes.byref(size),
            ):
                return ""
            # TOKEN_USER starts with a SID pointer.
            sid = ctypes.cast(buf, ctypes.POINTER(ctypes.c_void_p))[0]
            sid_str = ctypes.c_wchar_p()
            if not ctypes.windll.advapi32.ConvertSidToStringSidW(sid, ctypes.byref(sid_str)):  # type: ignore[attr-defined]
                return ""
            try:
                return sid_str.value or ""
            finally:
                if sid_str:
                    ctypes.windll.kernel32.LocalFree(sid_str)  # type: ignore[attr-defined]
        finally:
            ctypes.windll.kernel32.CloseHandle(token)  # type: ignore[attr-defined]
    except (AttributeError, OSError, TypeError, ValueError):
        return ""


def installing_username() -> str:
    """Return the Windows user who launched the elevated installer."""
    for key in ("USERNAME", "USER"):
        value = (os.environ.get(key) or "").strip()
        if value:
            return value
    return ""


def parse_icacls_failed_count(output: str) -> int | None:
    """Return `Failed processing N files` count from icacls output, if present."""
    match = _FAILED_PROCESSING_RE.search(output or "")
    if match is None:
        return None
    return int(match.group(1))


def parse_icacls_success_count(output: str) -> int | None:
    """Return `Successfully processed N files` count from icacls output, if present."""
    match = _SUCCESS_PROCESSING_RE.search(output or "")
    if match is None:
        return None
    return int(match.group(1))


def repair_install_tree_acls(target: Path, log: OutcomeLog) -> bool:
    """Reset protected child DACLs, then grant Full Control to the installing user.

    Offline `uv` hardlinks can leave package files with SYSTEM/Administrators-only
    DACLs that ignore parent `(OI)(CI)` inheritance. `/reset` restores inheritance;
    `/grant` alone cannot open those protected descriptors. `icacls /C` may exit 0
    even when some files fail — parse `Failed processing N files` and treat N>0
    as failure.

    """
    if sys.platform != "win32":
        log.add("skipped", "ACL repair skipped (not Windows)")
        return True
    if not target.exists():
        log.add("failed", f"ACL repair skipped: path missing ({target})")
        return False

    principal = installing_user_principal()
    if not principal:
        log.add("failed", "ACL repair skipped: USERNAME/SID not available")
        return False

    log.step("Repair folder permissions for the current user")
    log.detail(f"Target: {target}")
    log.detail(f"Principal: {principal}")

    ok = True
    if not _run_cmd(["attrib", "-R", str(target), "/S", "/D"], log, label="attrib -R"):
        # attrib can fail on locked files; keep going — ACL reset is the main fix.
        log.detail("attrib -R had errors (continuing)")

    reset = ["icacls", str(target), "/reset", "/T", "/C", "/Q"]
    if not _run_icacls(reset, log, label="icacls /reset"):
        log.detail("icacls /reset incomplete; trying takeown fallback…")
        _run_cmd(["takeown", "/F", str(target), "/R", "/D", "Y"], log, label="takeown /R")
        if not _run_icacls(reset, log, label="icacls /reset (after takeown)"):
            ok = False

    grant = ["icacls", str(target), "/grant", f"{principal}:(OI)(CI)F", "/T", "/C", "/Q"]
    if not _run_icacls(grant, log, label="icacls /grant"):
        ok = False

    # Also grant by username when principal was a SID, for clearer Explorer ACLs.
    user = installing_username()
    if user and principal.startswith("*"):
        grant_name = ["icacls", str(target), "/grant", f"{user}:(OI)(CI)F", "/T", "/C", "/Q"]
        if not _run_icacls(grant_name, log, label="icacls /grant (username)"):
            log.detail("Username grant failed (SID grant may still be enough)")

    integrity = ["icacls", str(target), "/setintegritylevel", "(OI)(CI)M", "/T", "/C", "/Q"]
    if not _run_icacls(integrity, log, label="icacls /setintegritylevel", allow_partial=True):
        log.detail("Medium integrity level could not be set (continuing)")

    if ok:
        log.add("installed", f"Reset ACLs and granted Full Control on {target}")
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


def _run_icacls(
    cmd: list[str],
    log: OutcomeLog,
    *,
    label: str,
    allow_partial: bool = False,
) -> bool:
    """Run icacls and fail when `Failed processing N files` reports N>0."""
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

    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}"
    failed = parse_icacls_failed_count(combined)
    success = parse_icacls_success_count(combined)
    if success is not None or failed is not None:
        log.detail(
            f"{label}: successfully={success if success is not None else '?'} "
            f"failed={failed if failed is not None else '?'}"
        )
    if failed is not None and failed > 0 and not allow_partial:
        sample = combined.strip()[:500]
        log.detail(f"{label}: Failed processing {failed} files" + (f" — {sample}" if sample else ""))
        return False
    if proc.returncode != 0 and not allow_partial:
        err = combined.strip()[:500]
        log.detail(f"{label} exit {proc.returncode}" + (f": {err}" if err else ""))
        return False
    return True


_TOKEN_QUERY = 0x0008
_TOKEN_USER = 1
