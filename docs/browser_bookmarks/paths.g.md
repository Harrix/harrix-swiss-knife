---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `backup_root`](#-function-backup_root)
- [🔧 Function `default_chrome_bookmarks_path`](#-function-default_chrome_bookmarks_path)
- [🔧 Function `default_yandex_bookmarks_path`](#-function-default_yandex_bookmarks_path)
- [🔧 Function `harrix_swiss_knife_data_dir`](#-function-harrix_swiss_knife_data_dir)
- [🔧 Function `is_chrome_running`](#-function-is_chrome_running)
- [🔧 Function `is_process_running`](#-function-is_process_running)
- [🔧 Function `is_yandex_running`](#-function-is_yandex_running)
- [🔧 Function `local_app_data`](#-function-local_app_data)
- [🔧 Function `running_browser_names`](#-function-running_browser_names)
- [🔧 Function `snapshot_path`](#-function-snapshot_path)

</details>

## 🔧 Function `backup_root`

```python
def backup_root() -> Path
```

Directory for timestamped Bookmarks backups.

<details>
<summary>Code:</summary>

```python
def backup_root() -> Path:
    return harrix_swiss_knife_data_dir() / "browser_bookmarks_backups"
```

</details>

## 🔧 Function `default_chrome_bookmarks_path`

```python
def default_chrome_bookmarks_path() -> Path
```

Default Chrome `Bookmarks` file for the Default profile.

<details>
<summary>Code:</summary>

```python
def default_chrome_bookmarks_path() -> Path:
    return local_app_data() / "Google" / "Chrome" / "User Data" / "Default" / "Bookmarks"
```

</details>

## 🔧 Function `default_yandex_bookmarks_path`

```python
def default_yandex_bookmarks_path() -> Path
```

Default Yandex Browser `Bookmarks` file for the Default profile.

<details>
<summary>Code:</summary>

```python
def default_yandex_bookmarks_path() -> Path:
    return local_app_data() / "Yandex" / "YandexBrowser" / "User Data" / "Default" / "Bookmarks"
```

</details>

## 🔧 Function `harrix_swiss_knife_data_dir`

```python
def harrix_swiss_knife_data_dir() -> Path
```

Per-user data directory outside the Git repo.

<details>
<summary>Code:</summary>

```python
def harrix_swiss_knife_data_dir() -> Path:
    if sys.platform == "win32":
        return local_app_data() / "HarrixSwissKnife"
    return local_app_data() / "harrix-swiss-knife"
```

</details>

## 🔧 Function `is_chrome_running`

```python
def is_chrome_running() -> bool
```

Return whether Google Chrome is running.

<details>
<summary>Code:</summary>

```python
def is_chrome_running() -> bool:
    return is_process_running(_CHROME_PROCESS)
```

</details>

## 🔧 Function `is_process_running`

```python
def is_process_running(image_name: str) -> bool
```

Return whether a Windows process with `image_name` is running.

<details>
<summary>Code:</summary>

```python
def is_process_running(image_name: str) -> bool:
    if sys.platform != "win32":
        return False
    tasklist = shutil.which("tasklist")
    if not tasklist:
        return False
    result = subprocess.run(
        [tasklist, "/FI", f"IMAGENAME eq {image_name}", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    return image_name.casefold() in (result.stdout or "").casefold()
```

</details>

## 🔧 Function `is_yandex_running`

```python
def is_yandex_running() -> bool
```

Return whether Yandex Browser (`browser.exe`) is running.

<details>
<summary>Code:</summary>

```python
def is_yandex_running() -> bool:
    return is_process_running(_YANDEX_PROCESS)
```

</details>

## 🔧 Function `local_app_data`

```python
def local_app_data() -> Path
```

Return the Windows LocalAppData directory (or a home fallback).

<details>
<summary>Code:</summary>

```python
def local_app_data() -> Path:
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            local = str(Path.home() / "AppData" / "Local")
        return Path(local)
    xdg = os.environ.get("XDG_DATA_HOME")
    return Path(xdg) if xdg else Path.home() / ".local" / "share"
```

</details>

## 🔧 Function `running_browser_names`

```python
def running_browser_names() -> list[str]
```

Return display names of browsers that are currently running.

<details>
<summary>Code:</summary>

```python
def running_browser_names() -> list[str]:
    names: list[str] = []
    if is_chrome_running():
        names.append("Google Chrome")
    if is_yandex_running():
        names.append("Yandex Browser")
    return names
```

</details>

## 🔧 Function `snapshot_path`

```python
def snapshot_path() -> Path
```

Path to the sync snapshot JSON (never under the Git repo).

<details>
<summary>Code:</summary>

```python
def snapshot_path() -> Path:
    return harrix_swiss_knife_data_dir() / "browser_bookmarks_sync.json"
```

</details>
