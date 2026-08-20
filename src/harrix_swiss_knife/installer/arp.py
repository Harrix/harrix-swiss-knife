"""Register / unregister Harrix Swiss Knife in Windows Apps & Features."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if sys.platform == "win32":
    import winreg
else:  # pragma: no cover
    winreg = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from pathlib import Path

    from harrix_swiss_knife.installer.log import OutcomeLog

ARP_KEY_NAME = "HarrixSwissKnife"
_UNINSTALL_SUBKEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"


def register_uninstall(
    *,
    install_root: Path,
    hsk_path: Path,
    version: str,
    publisher: str = "Harrix",
    display_name: str = "Harrix Swiss Knife",
    log: OutcomeLog | None = None,
) -> bool:
    """Write the HKLM Uninstall key used by Apps & Features."""
    if winreg is None:
        if log is not None:
            log.add("skipped", "Apps & Features registration skipped (not Windows)")
        return False

    pyw = hsk_path / ".venv" / "Scripts" / "pythonw.exe"
    launch = hsk_path / "launch_uninstall.py"
    uninstall = f'"{pyw}" "{launch}"'
    quiet = f'"{pyw}" "{launch}" --silent'
    icon = _display_icon(hsk_path)
    install_date = datetime.now(tz=UTC).astimezone().strftime("%Y%m%d")

    try:
        with winreg.CreateKeyEx(
            winreg.HKEY_LOCAL_MACHINE,
            f"{_UNINSTALL_SUBKEY}\\{ARP_KEY_NAME}",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, display_name)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, publisher)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version or "unknown")
            winreg.SetValueEx(key, "InstallDate", 0, winreg.REG_SZ, install_date)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_root))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall)
            winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ, quiet)
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            if icon:
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon)
    except OSError as exc:
        if log is not None:
            log.add("failed", f"Apps & Features registration failed: {exc}")
        return False
    if log is not None:
        log.add("installed", "Registered in Apps & Features")
    return True


def unregister_uninstall(log: OutcomeLog | None = None) -> bool:
    """Remove the HKLM Uninstall key. Returns whether the key is gone."""
    if winreg is None:
        if log is not None:
            log.add("skipped", "Apps & Features unregister skipped (not Windows)")
        return True
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, f"{_UNINSTALL_SUBKEY}\\{ARP_KEY_NAME}")
    except FileNotFoundError:
        if log is not None:
            log.add("already", "Apps & Features entry already absent")
        return True
    except OSError as exc:
        if log is not None:
            log.add("failed", f"Apps & Features unregister failed: {exc}")
        return False
    if log is not None:
        log.add("installed", "Removed Apps & Features entry")
    return True


def _display_icon(hsk_path: Path) -> str:
    for candidate in (
        hsk_path / "resources" / "icons" / "app.ico",
        hsk_path / "src" / "harrix_swiss_knife" / "resources" / "icons" / "app.ico",
        hsk_path / ".venv" / "Scripts" / "harrix-swiss-knife.exe",
        hsk_path / ".venv" / "Scripts" / "pythonw.exe",
    ):
        if candidate.is_file():
            return str(candidate)
    return ""
