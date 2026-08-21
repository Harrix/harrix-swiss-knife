---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `uv_locate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `find_uv_exe`](#-function-find_uv_exe)
- [🔧 Function `refresh_path`](#-function-refresh_path)

</details>

## 🔧 Function `find_uv_exe`

```python
def find_uv_exe() -> Path | None
```

Locate the `uv` executable on PATH or common install locations.

Installer and standalone installs often put `uv` in `~/.local/bin`. Tray apps
launched from Explorer shortcuts may not see an updated user PATH, so this
also checks well-known directories.

<details>
<summary>Code:</summary>

```python
def find_uv_exe() -> Path | None:
    which = shutil.which("uv")
    if which:
        return Path(which)

    home = Path.home()
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    candidates = [
        home / ".local" / "bin" / ("uv.exe" if sys.platform == "win32" else "uv"),
        local / "Programs" / "uv" / "uv.exe",
        local / "Microsoft" / "WinGet" / "Links" / "uv.exe",
        local / "Microsoft" / "WindowsApps" / "uv.exe",
        _program_files() / "uv" / "uv.exe",
        _program_files_x86() / "uv" / "uv.exe",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None
```

</details>

## 🔧 Function `refresh_path`

```python
def refresh_path() -> None
```

Refresh process PATH from the environment and Windows registry.

Expands `%VAR%` segments from registry values so entries like
`%USERPROFILE%\.local\bin` resolve for `shutil.which` / subprocess.

<details>
<summary>Code:</summary>

```python
def refresh_path() -> None:
    machine = os.environ.get("Path", "")  # noqa: SIM112
    user = ""
    if winreg is not None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                user, _ = winreg.QueryValueEx(key, "Path")
        except OSError:
            user = os.environ.get("Path", "")  # noqa: SIM112
    else:
        user = os.environ.get("Path", "")  # noqa: SIM112
    parts = [p for p in (machine, user) if p]
    if winreg is not None:
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            ) as key:
                machine_reg, _ = winreg.QueryValueEx(key, "Path")
                parts = [machine_reg, user]
        except OSError:
            pass
    combined = ";".join(parts)
    if sys.platform == "win32":
        combined = os.path.expandvars(combined)
    os.environ["Path"] = combined  # noqa: SIM112
```

</details>
