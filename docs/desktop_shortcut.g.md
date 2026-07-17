---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `desktop_shortcut.py`

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
```

</details>
