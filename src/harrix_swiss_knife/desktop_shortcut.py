"""Create Windows shortcuts for Harrix Swiss Knife (installer / tray Dev action)."""

from __future__ import annotations

import contextlib
import ctypes
import shutil
import sys
from pathlib import Path

# Desktop / Startup .lnk pointing at the GUI entry or pythonw.exe + launcher
SHORTCUT_NAME = "Harrix Swiss Knife.lnk"
UNINSTALL_SHORTCUT_NAME = "Uninstall Harrix Swiss Knife.lnk"
_STAGING_NAME = ".hsk_desktop_shortcut_build.lnk"
_UNINSTALL_STAGING_NAME = ".hsk_uninstall_shortcut_build.lnk"
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


def create_uninstall_shortcut(project_root: Path) -> Path:
    """Create or update a desktop shortcut that launches the uninstall wizard.

    Raises:

    - `OSError`: On non-Windows platforms or when shortcut creation fails.

    """
    if sys.platform != "win32":
        msg = "Uninstall shortcut is only supported on Windows"
        raise OSError(msg)

    root = project_root.resolve()
    pyw = root / ".venv" / "Scripts" / "pythonw.exe"
    launch_py = root / "launch_uninstall.py"
    if not pyw.is_file():
        msg = f"pythonw.exe not found: {pyw}"
        raise OSError(msg)
    if not launch_py.is_file():
        msg = f"launch_uninstall.py not found: {launch_py}"
        raise OSError(msg)

    destination = _get_shell_folder(_CSIDL_DESKTOPDIRECTORY, "Desktop")
    final_lnk = destination / UNINSTALL_SHORTCUT_NAME
    staging = root / "temp" / _UNINSTALL_STAGING_NAME
    staging.parent.mkdir(parents=True, exist_ok=True)
    try:
        _write_shortcut_file(
            staging,
            target=pyw,
            arguments=f'"{launch_py}"',
            working_directory=root,
            description="Uninstall Harrix Swiss Knife (keeps databases)",
            icon_location=_resolve_icon_location(root),
        )
        if final_lnk.exists():
            final_lnk.unlink()
        shutil.move(str(staging), str(final_lnk))
    except Exception as e:
        msg = f"Could not create uninstall shortcut: {e}"
        raise OSError(msg) from e
    finally:
        if staging.exists():
            staging.unlink(missing_ok=True)

    if not final_lnk.is_file():
        msg = f"Shortcut file was not created: {final_lnk}"
        raise OSError(msg)
    return final_lnk


def remove_app_shortcuts() -> list[Path]:
    """Delete desktop, startup, and uninstall shortcuts. Return paths that were removed."""
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


def _create_app_shortcut(project_root: Path, *, destination: Path, kind: str) -> Path:
    if sys.platform != "win32":
        msg = f"{kind} shortcut is only supported on Windows"
        raise OSError(msg)

    root = project_root.resolve()
    scripts = root / ".venv" / "Scripts"
    gui_exe = scripts / "harrix-swiss-knife.exe"
    pyw = scripts / "pythonw.exe"
    launch_py = root / "launch_tray.py"
    main_py = root / "src" / "harrix_swiss_knife" / "main.py"

    if gui_exe.is_file():
        target = gui_exe
        arguments = ""
    elif pyw.is_file() and launch_py.is_file():
        target = pyw
        arguments = f'"{launch_py}"'
    elif pyw.is_file() and main_py.is_file():
        target = pyw
        arguments = f'"{main_py}"'
    else:
        if not pyw.is_file():
            msg = f"pythonw.exe not found: {pyw}"
            raise OSError(msg)
        msg = f"Launcher not found (expected {launch_py} or {main_py})"
        raise OSError(msg)

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
