"""Create Windows shortcuts for Harrix Swiss Knife (installer / tray Dev action)."""

from __future__ import annotations

import contextlib
import ctypes
import shutil
import sys
from pathlib import Path

# Desktop / Startup .lnk pointing at pythonw.exe + launcher
SHORTCUT_NAME = "Harrix Swiss Knife.lnk"
# Older installs put an uninstall shortcut on the Desktop; it is only cleaned up now.
UNINSTALL_SHORTCUT_NAME = "Uninstall Harrix Swiss Knife.lnk"
_STAGING_NAME = ".hsk_desktop_shortcut_build.lnk"
_CSIDL_DESKTOPDIRECTORY = 0x10
_CSIDL_STARTUP = 0x07


def create_desktop_shortcut(project_root: Path) -> Path:
    """Create or update the desktop shortcut. Returns the path to the `.lnk` file.

    The shortcut is built in the project `temp/` folder first, then moved to the Desktop.
    That avoids COM encoding issues when the Desktop path contains non-ASCII characters.

    Raises:

    - `OSError`: On non-Windows platforms or when shortcut creation fails.

    """
    return _create_app_shortcut(
        project_root,
        destination=_get_shell_folder(_CSIDL_DESKTOPDIRECTORY, "Desktop"),
        kind="Desktop",
    )


def create_startup_shortcut(project_root: Path) -> Path:
    """Create or update the Startup-folder shortcut for Windows autostart.

    Same target/args/cwd/icon as the desktop shortcut. Returns the `.lnk` path.

    Raises:

    - `OSError`: On non-Windows platforms or when shortcut creation fails.

    """
    return _create_app_shortcut(
        project_root,
        destination=_get_shell_folder(_CSIDL_STARTUP, "Startup"),
        kind="Startup",
    )


def remove_app_shortcuts() -> list[Path]:
    """Delete desktop, startup, and legacy uninstall shortcuts. Return paths that were removed."""
    if sys.platform != "win32":
        return []
    removed: list[Path] = []
    targets: list[Path] = []
    with contextlib.suppress(OSError):
        desktop = _get_shell_folder(_CSIDL_DESKTOPDIRECTORY, "Desktop")
        targets.append(desktop / SHORTCUT_NAME)
        targets.append(desktop / UNINSTALL_SHORTCUT_NAME)
    with contextlib.suppress(OSError):
        targets.append(_get_shell_folder(_CSIDL_STARTUP, "Startup") / SHORTCUT_NAME)
    for path in targets:
        if not path.is_file():
            continue
        try:
            path.unlink()
            removed.append(path)
        except OSError:
            continue
    return removed


def remove_desktop_uninstall_shortcut() -> Path | None:
    """Delete the legacy desktop uninstall shortcut. Return its path when removed."""
    if sys.platform != "win32":
        return None
    with contextlib.suppress(OSError):
        lnk = _get_shell_folder(_CSIDL_DESKTOPDIRECTORY, "Desktop") / UNINSTALL_SHORTCUT_NAME
        if lnk.is_file():
            lnk.unlink()
            return lnk
    return None


def _create_app_shortcut(project_root: Path, *, destination: Path, kind: str) -> Path:
    if sys.platform != "win32":
        msg = f"{kind} shortcut is only supported on Windows"
        raise OSError(msg)

    root = project_root.resolve()
    scripts = root / ".venv" / "Scripts"
    pyw = scripts / "pythonw.exe"
    launch_py = root / "launch_tray.py"
    main_py = root / "src" / "harrix_swiss_knife" / "main.py"

    # `pythonw.exe launch_tray.py` is preferred over the generated
    # `harrix-swiss-knife.exe` wrapper: it puts `src/` on `sys.path` and shows a
    # dialog plus `startup-crash.log` when the import fails.
    if not pyw.is_file():
        msg = f"pythonw.exe not found: {pyw}"
        raise OSError(msg)
    if launch_py.is_file():
        launcher = launch_py
    elif main_py.is_file():
        launcher = main_py
    else:
        msg = f"Launcher not found (expected {launch_py} or {main_py})"
        raise OSError(msg)
    target = pyw
    arguments = f'"{launcher}"'

    if not destination.is_dir():
        msg = f"{kind} folder not found: {destination}"
        raise OSError(msg)

    final_lnk = destination / SHORTCUT_NAME
    staging = root / "temp" / _STAGING_NAME
    staging.parent.mkdir(parents=True, exist_ok=True)

    try:
        _write_shortcut_file(
            staging,
            target=target,
            arguments=arguments,
            working_directory=root,
            description="Harrix Swiss Knife",
            icon_location=_resolve_icon_location(root),
        )
        if final_lnk.exists():
            final_lnk.unlink()
        shutil.move(str(staging), str(final_lnk))
    except Exception as e:
        msg = f"Could not create {kind.lower()} shortcut: {e}"
        raise OSError(msg) from e
    finally:
        if staging.exists():
            staging.unlink(missing_ok=True)

    if not final_lnk.is_file():
        msg = f"Shortcut file was not created: {final_lnk}"
        raise OSError(msg)
    return final_lnk


def _get_shell_folder(csidl: int, label: str) -> Path:
    """Return a special folder path via SHGetFolderPathW (wide-char)."""
    buf = ctypes.create_unicode_buffer(260)
    if ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf) != 0:
        msg = f"{label} folder not found"
        raise OSError(msg)
    return Path(buf.value)


def _resolve_icon_location(project_root: Path) -> str | None:
    for rel in ("src/harrix_swiss_knife/assets/app.ico", "img/icon.ico"):
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
    """Write a `.lnk` file via WScript.Shell (pythonnet + late-bound COM)."""
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
