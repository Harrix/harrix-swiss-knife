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
- [🔧 Function `remove_app_shortcuts`](#-function-remove_app_shortcuts)
- [🔧 Function `remove_desktop_uninstall_shortcut`](#-function-remove_desktop_uninstall_shortcut)

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

## 🔧 Function `remove_app_shortcuts`

```python
def remove_app_shortcuts() -> list[Path]
```

Delete desktop, startup, and legacy uninstall shortcuts. Return paths that were removed.

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

## 🔧 Function `remove_desktop_uninstall_shortcut`

```python
def remove_desktop_uninstall_shortcut() -> Path | None
```

Delete the legacy desktop uninstall shortcut. Return its path when removed.

<details>
<summary>Code:</summary>

```python
def remove_desktop_uninstall_shortcut() -> Path | None:
    if sys.platform != "win32":
        return None
    with contextlib.suppress(OSError):
        lnk = _get_shell_folder(_CSIDL_DESKTOPDIRECTORY, "Desktop") / UNINSTALL_SHORTCUT_NAME
        if lnk.is_file():
            lnk.unlink()
            return lnk
    return None
```

</details>
