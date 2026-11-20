---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `uv_upgrade_resume.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `UvUpgradeResume`](#%EF%B8%8F-class-uvupgraderesume)
- [🔧 Function `clear_cursor_terminal_resume_flag`](#-function-clear_cursor_terminal_resume_flag)
- [🔧 Function `clear_uv_upgrade_resume`](#-function-clear_uv_upgrade_resume)
- [🔧 Function `cursor_terminal_resume_flag_path`](#-function-cursor_terminal_resume_flag_path)
- [🔧 Function `normalize_uv_upgrade_resume`](#-function-normalize_uv_upgrade_resume)
- [🔧 Function `pop_uv_upgrade_resume`](#-function-pop_uv_upgrade_resume)
- [🔧 Function `save_uv_upgrade_resume`](#-function-save_uv_upgrade_resume)
- [🔧 Function `write_cursor_terminal_resume_flag`](#-function-write_cursor_terminal_resume_flag)

</details>

## 🏛️ Class `UvUpgradeResume`

```python
class UvUpgradeResume(TypedDict)
```

What to restore after the detached uv upgrade relaunches HSK.

<details>
<summary>Code:</summary>

```python
class UvUpgradeResume(TypedDict):

    reopen_maintenance_checklist: bool
    maintenance_session_done: list[str]
```

</details>

## 🔧 Function `clear_cursor_terminal_resume_flag`

```python
def clear_cursor_terminal_resume_flag(project_root: Path | None = None) -> None
```

Remove the folderOpen flag that starts HSK inside Cursor's terminal.

<details>
<summary>Code:</summary>

```python
def clear_cursor_terminal_resume_flag(project_root: Path | None = None) -> None:
    path = cursor_terminal_resume_flag_path(project_root)
    path.unlink(missing_ok=True)
```

</details>

## 🔧 Function `clear_uv_upgrade_resume`

```python
def clear_uv_upgrade_resume() -> None
```

Remove a leftover resume payload without applying it.

<details>
<summary>Code:</summary>

```python
def clear_uv_upgrade_resume() -> None:
    try:
        loaded: dict[str, Any] = h.dev.config_load(get_config_path_str(), is_temp=True)
    except Exception:
        return
    if _RESUME_KEY not in loaded:
        return
    loaded.pop(_RESUME_KEY, None)
    h.dev.config_save(loaded, get_config_path_str(), is_temp=True)
```

</details>

## 🔧 Function `cursor_terminal_resume_flag_path`

```python
def cursor_terminal_resume_flag_path(project_root: Path | None = None) -> Path
```

Return `temp/hsk-resume-after-uv-upgrade.flag` under the project root.

<details>
<summary>Code:</summary>

```python
def cursor_terminal_resume_flag_path(project_root: Path | None = None) -> Path:
    root = project_root if project_root is not None else get_project_root()
    return root.resolve() / "temp" / CURSOR_TERMINAL_RESUME_FLAG_NAME
```

</details>

## 🔧 Function `normalize_uv_upgrade_resume`

```python
def normalize_uv_upgrade_resume(raw: object) -> UvUpgradeResume | None
```

Return a typed resume payload, or `None` when `raw` is invalid.

<details>
<summary>Code:</summary>

```python
def normalize_uv_upgrade_resume(raw: object) -> UvUpgradeResume | None:
    if not isinstance(raw, dict):
        return None
    reopen = bool(raw.get("reopen_maintenance_checklist"))
    done_raw = raw.get("maintenance_session_done")
    done: list[str] = []
    if isinstance(done_raw, list):
        done = [str(item) for item in done_raw if isinstance(item, str) and item.strip()]
    if reopen and _UPGRADE_STEP_CLASS not in done:
        done.append(_UPGRADE_STEP_CLASS)
    return {
        "reopen_maintenance_checklist": reopen,
        "maintenance_session_done": done,
    }
```

</details>

## 🔧 Function `pop_uv_upgrade_resume`

```python
def pop_uv_upgrade_resume() -> UvUpgradeResume | None
```

Load and clear the pending resume payload, or `None` when absent.

<details>
<summary>Code:</summary>

```python
def pop_uv_upgrade_resume() -> UvUpgradeResume | None:
    try:
        loaded: dict[str, Any] = h.dev.config_load(get_config_path_str(), is_temp=True)
    except Exception:
        return None
    raw = loaded.pop(_RESUME_KEY, None)
    if raw is None:
        return None
    try:
        h.dev.config_save(loaded, get_config_path_str(), is_temp=True)
    except Exception:
        return None
    return normalize_uv_upgrade_resume(raw)
```

</details>

## 🔧 Function `save_uv_upgrade_resume`

```python
def save_uv_upgrade_resume(*, reopen_maintenance_checklist: bool, maintenance_session_done: list[str] | None = None) -> None
```

Store resume intent for the next HSK process after uv upgrade.

<details>
<summary>Code:</summary>

```python
def save_uv_upgrade_resume(
    *,
    reopen_maintenance_checklist: bool,
    maintenance_session_done: list[str] | None = None,
) -> None:
    done = list(maintenance_session_done or [])
    if reopen_maintenance_checklist and _UPGRADE_STEP_CLASS not in done:
        done.append(_UPGRADE_STEP_CLASS)
    payload: UvUpgradeResume = {
        "reopen_maintenance_checklist": reopen_maintenance_checklist,
        "maintenance_session_done": done,
    }
    h.dev.config_update_value(_RESUME_KEY, payload, get_config_path_str(), is_temp=True)
```

</details>

## 🔧 Function `write_cursor_terminal_resume_flag`

```python
def write_cursor_terminal_resume_flag(project_root: Path | None = None) -> Path
```

Create the flag that makes Cursor's folderOpen task start HSK in a terminal.

<details>
<summary>Code:</summary>

```python
def write_cursor_terminal_resume_flag(project_root: Path | None = None) -> Path:
    path = cursor_terminal_resume_flag_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("1\n", encoding="utf-8")
    return path
```

</details>
