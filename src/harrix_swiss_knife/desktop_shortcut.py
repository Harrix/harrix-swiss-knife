"""Create Windows desktop shortcut for Harrix Swiss Knife (install/harrix-swiss-knife.ps1 logic)."""

from __future__ import annotations

import ctypes
import shutil
import sys
from pathlib import Path

# Mirrors New-DesktopShortcut in install/harrix-swiss-knife.ps1
_SHORTCUT_NAME = "Harrix Swiss Knife.lnk"
_STAGING_NAME = ".hsk_desktop_shortcut_build.lnk"
_CSIDL_DESKTOPDIRECTORY = 0x10


def create_desktop_shortcut(project_root: Path) -> Path:
    """Create or update the desktop shortcut. Returns the path to the ``.lnk`` file.

    The shortcut is built in the project ``temp/`` folder first, then moved to the Desktop.
    That avoids COM encoding issues when the Desktop path contains non-ASCII characters.

    Raises:

    - `OSError`: On non-Windows platforms or when shortcut creation fails.

    """
    if sys.platform != "win32":
        msg = "Desktop shortcut is only supported on Windows"
        raise OSError(msg)

    root = project_root.resolve()
    pyw = root / ".venv" / "Scripts" / "pythonw.exe"
    main_py = root / "src" / "harrix_swiss_knife" / "main.py"
    if not pyw.is_file():
        msg = f"pythonw.exe not found: {pyw}"
        raise OSError(msg)
    if not main_py.is_file():
        msg = f"main.py not found: {main_py}"
        raise OSError(msg)

    desktop = _get_desktop_directory()
    if not desktop.is_dir():
        msg = f"Desktop folder not found: {desktop}"
        raise OSError(msg)

    final_lnk = desktop / _SHORTCUT_NAME
    staging = root / "temp" / _STAGING_NAME
    staging.parent.mkdir(parents=True, exist_ok=True)

    try:
        _write_shortcut_file(
            staging,
            target=pyw,
            arguments=f'"{main_py}"',
            working_directory=root,
            description="Harrix Swiss Knife",
            icon_location=_resolve_icon_location(root),
        )
        if final_lnk.exists():
            final_lnk.unlink()
        shutil.move(str(staging), str(final_lnk))
    except Exception as e:
        msg = f"Could not create desktop shortcut: {e}"
        raise OSError(msg) from e
    finally:
        if staging.exists():
            staging.unlink(missing_ok=True)

    if not final_lnk.is_file():
        msg = f"Shortcut file was not created: {final_lnk}"
        raise OSError(msg)
    return final_lnk


def _get_desktop_directory() -> Path:
    """Return the physical Desktop folder (SHGetFolderPathW, wide-char)."""
    buf = ctypes.create_unicode_buffer(260)
    if ctypes.windll.shell32.SHGetFolderPathW(None, _CSIDL_DESKTOPDIRECTORY, None, 0, buf) != 0:
        msg = "Desktop folder not found"
        raise OSError(msg)
    return Path(buf.value)


def _resolve_icon_location(project_root: Path) -> str | None:
    for rel in ("img/icon.ico", "src/harrix_swiss_knife/assets/app.ico"):
        icon = project_root / rel
        if icon.is_file():
            return f"{icon},0"
    return None


def _write_shortcut_file(
    lnk_path: Path,
    *,
    target: Path,
    arguments: str,
    working_directory: Path,
    description: str,
    icon_location: str | None,
) -> None:
    """Write a ``.lnk`` file via WScript.Shell (pythonnet + late-bound COM)."""
    import clr  # noqa: PLC0415

    clr.AddReference("System")
    from System import Activator, Type  # type: ignore # noqa: PGH003, PLC0415
    from System.Reflection import BindingFlags  # type: ignore # noqa: PGH003, PLC0415

    shell = Activator.CreateInstance(Type.GetTypeFromProgID("WScript.Shell"))
    shortcut = shell.GetType().InvokeMember(
        "CreateShortcut",
        BindingFlags.InvokeMethod,
        None,
        shell,
        [str(lnk_path)],
    )
    props: list[tuple[str, object]] = [
        ("TargetPath", str(target)),
        ("Arguments", arguments),
        ("WorkingDirectory", str(working_directory)),
        ("WindowStyle", 1),
        ("Description", description),
    ]
    if icon_location:
        props.append(("IconLocation", icon_location))
    for name, value in props:
        shortcut.GetType().InvokeMember(
            name,
            BindingFlags.SetProperty,
            None,
            shortcut,
            [value],
        )
    shortcut.GetType().InvokeMember("Save", BindingFlags.InvokeMethod, None, shortcut, [])
