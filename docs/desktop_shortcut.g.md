---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `desktop_shortcut.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `create_desktop_shortcut`](#-function-create_desktop_shortcut)
- [🔧 Function `create_startup_shortcut`](#-function-create_startup_shortcut)
- [🔧 Function `create_uninstall_shortcut`](#-function-create_uninstall_shortcut)
- [🔧 Function `remove_app_shortcuts`](#-function-remove_app_shortcuts)

</details>

## 🔧 Function `create_desktop_shortcut`

```python
def create_desktop_shortcut(project_root: Path) -> Path
```

Create or update the desktop shortcut. Returns the path to the `.lnk` file.

The shortcut is built in the project `temp/` folder first, then moved to the Desktop.
That avoids COM encoding issues when the Desktop path contains non-ASCII characters.

Raises:

- `OSError`: On non-Windows platforms or when shortcut creation fails.

<details>
<summary>Code:</summary>

```python
def create_desktop_shortcut(project_root: Path) -> Path:
    return _create_app_shortcut(
        project_root,
        destination=_get_shell_folder(_CSIDL_DESKTOPDIRECTORY, "Desktop"),
        kind="Desktop",
    )
```

</details>

## 🔧 Function `create_startup_shortcut`

```python
def create_startup_shortcut(project_root: Path) -> Path
```

Create or update the Startup-folder shortcut for Windows autostart.

Same target/args/cwd/icon as the desktop shortcut. Returns the `.lnk` path.

Raises:

- `OSError`: On non-Windows platforms or when shortcut creation fails.

<details>
<summary>Code:</summary>

```python
def create_startup_shortcut(project_root: Path) -> Path:
    return _create_app_shortcut(
        project_root,
        destination=_get_shell_folder(_CSIDL_STARTUP, "Startup"),
        kind="Startup",
    )
```

</details>

## 🔧 Function `create_uninstall_shortcut`

```python
def create_uninstall_shortcut(project_root: Path) -> Path
```

Create or update a desktop shortcut that launches the uninstall wizard.

Raises:

- `OSError`: On non-Windows platforms or when shortcut creation fails.

<details>
<summary>Code:</summary>

```python
def create_uninstall_shortcut(project_root: Path) -> Path:
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
```

</details>

## 🔧 Function `remove_app_shortcuts`

```python
def remove_app_shortcuts() -> list[Path]
```

Delete desktop, startup, and uninstall shortcuts. Return paths that were removed.

<details>
<summary>Code:</summary>

```python
def remove_app_shortcuts() -> list[Path]:
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
```

</details>
