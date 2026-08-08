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
