---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `maintenance_checklist_steps.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MaintenanceStep`](#%EF%B8%8F-class-maintenancestep)
  - [⚙️ Method `class_name (property)`](#%EF%B8%8F-method-class_name-property)
  - [⚙️ Method `title (property)`](#%EF%B8%8F-method-title-property)
- [🏛️ Class `MaintenanceStepSpec`](#%EF%B8%8F-class-maintenancestepspec)
- [🔧 Function `format_last_used`](#-function-format_last_used)
- [🔧 Function `is_last_used_within`](#-function-is_last_used_within)
- [🔧 Function `last_used_for_class`](#-function-last_used_for_class)
- [🔧 Function `load_git_repos_all_clean`](#-function-load_git_repos_all_clean)
- [🔧 Function `load_py_check_all_passed`](#-function-load_py_check_all_passed)
- [🔧 Function `load_show_update_hsk_step`](#-function-load_show_update_hsk_step)
- [🔧 Function `maintenance_groups`](#-function-maintenance_groups)
- [🔧 Function `maintenance_steps`](#-function-maintenance_steps)
- [🔧 Function `save_git_repos_all_clean`](#-function-save_git_repos_all_clean)
- [🔧 Function `save_py_check_all_passed`](#-function-save_py_check_all_passed)
- [🔧 Function `save_show_update_hsk_step`](#-function-save_show_update_hsk_step)

</details>

## 🏛️ Class `MaintenanceStep`

```python
class MaintenanceStep
```

One resolved row in the maintenance checklist.

<details>
<summary>Code:</summary>

```python
class MaintenanceStep:

    action_cls: type[ActionBase]
    group: str
    lucide_icon: str
    note: str = ""
    include_in_run_all: bool = True
    title_override: str | None = None

    @property
    def class_name(self) -> str:
        """Action class name used in `action_usage.json`."""
        return self.action_cls.__name__

    @property
    def title(self) -> str:
        """Display title for the checklist row."""
        if self.title_override:
            return self.title_override
        raw = getattr(self.action_cls, "title", self.class_name)
        return str(raw).replace("`", "")
```

</details>

### ⚙️ Method `class_name (property)`

```python
def class_name(self) -> str
```

Action class name used in `action_usage.json`.

<details>
<summary>Code:</summary>

```python
def class_name(self) -> str:
        return self.action_cls.__name__
```

</details>

### ⚙️ Method `title (property)`

```python
def title(self) -> str
```

Display title for the checklist row.

<details>
<summary>Code:</summary>

```python
def title(self) -> str:
        if self.title_override:
            return self.title_override
        raw = getattr(self.action_cls, "title", self.class_name)
        return str(raw).replace("`", "")
```

</details>

## 🏛️ Class `MaintenanceStepSpec`

```python
class MaintenanceStepSpec
```

Declarative checklist row (action imported lazily).

<details>
<summary>Code:</summary>

```python
class MaintenanceStepSpec:

    module: str
    class_name: str
    group: str
    lucide_icon: str
    note: str = ""
    include_in_run_all: bool = True
    title_override: str | None = None
```

</details>

## 🔧 Function `format_last_used`

```python
def format_last_used(iso_stamp: str | None) -> str
```

Return a short relative or absolute label for a usage timestamp.

<details>
<summary>Code:</summary>

```python
def format_last_used(iso_stamp: str | None) -> str:
    parsed = _parse_last_used(iso_stamp)
    if parsed is None:
        return "Never" if not iso_stamp or not str(iso_stamp).strip() else str(iso_stamp)
    now = datetime.now(UTC).astimezone()
    local = parsed.astimezone()
    delta = now - local
    seconds = int(delta.total_seconds())
    if seconds < 0:
        return local.strftime("%Y-%m-%d %H:%M")
    if seconds < _SECONDS_PER_MINUTE:
        return "Just now"
    if seconds < _SECONDS_PER_HOUR:
        minutes = seconds // _SECONDS_PER_MINUTE
        return f"{minutes} min ago"
    if seconds < _SECONDS_PER_DAY:
        hours = seconds // _SECONDS_PER_HOUR
        return f"{hours} h ago"
    if seconds < _SECONDS_PER_DAY * _RELATIVE_WEEK_DAYS:
        days = seconds // _SECONDS_PER_DAY
        return f"{days} d ago"
    return local.strftime("%Y-%m-%d %H:%M")
```

</details>

## 🔧 Function `is_last_used_within`

```python
def is_last_used_within(iso_stamp: str | None, *, hours: float = 24) -> bool
```

Return whether `iso_stamp` falls within the last `hours` (inclusive of now).

<details>
<summary>Code:</summary>

```python
def is_last_used_within(iso_stamp: str | None, *, hours: float = 24) -> bool:
    parsed = _parse_last_used(iso_stamp)
    if parsed is None or hours <= 0:
        return False
    now = datetime.now(UTC).astimezone()
    seconds = (now - parsed.astimezone()).total_seconds()
    return 0 <= seconds < hours * _SECONDS_PER_HOUR
```

</details>

## 🔧 Function `last_used_for_class`

```python
def last_used_for_class(class_name: str) -> str
```

Return the ISO `last_used` stamp for [`class_name`](#%EF%B8%8F-method-class_name-property), or empty string.

<details>
<summary>Code:</summary>

```python
def last_used_for_class(class_name: str) -> str:
    entry = load_action_usage().get(class_name)
    if entry is None:
        return ""
    return entry.get("last_used") or ""
```

</details>

## 🔧 Function `load_git_repos_all_clean`

```python
def load_git_repos_all_clean() -> bool | None
```

Return last Git-check result for the checklist tint, or `None` if unknown.

<details>
<summary>Code:</summary>

```python
def load_git_repos_all_clean() -> bool | None:
    return _load_temp_bool(_GIT_REPOS_ALL_CLEAN_KEY)
```

</details>

## 🔧 Function `load_py_check_all_passed`

```python
def load_py_check_all_passed() -> bool | None
```

Return last Full PY check result for the checklist tint, or `None` if unknown.

<details>
<summary>Code:</summary>

```python
def load_py_check_all_passed() -> bool | None:
    return _load_temp_bool(_PY_CHECK_ALL_PASSED_KEY)
```

</details>

## 🔧 Function `load_show_update_hsk_step`

```python
def load_show_update_hsk_step() -> bool
```

Return whether the Update HSK checklist row is visible (default: hidden).

<details>
<summary>Code:</summary>

```python
def load_show_update_hsk_step() -> bool:
    try:
        loaded: dict[str, Any] = h.dev.config_load(get_config_path_str(), is_temp=True)
    except Exception:
        return False
    value = loaded.get(_SHOW_UPDATE_HSK_KEY, False)
    return value if isinstance(value, bool) else False
```

</details>

## 🔧 Function `maintenance_groups`

```python
def maintenance_groups() -> list[tuple[str, list[MaintenanceStep]]]
```

Group resolved steps preserving order.

<details>
<summary>Code:</summary>

```python
def maintenance_groups() -> list[tuple[str, list[MaintenanceStep]]]:
    groups: list[tuple[str, list[MaintenanceStep]]] = []
    index: dict[str, list[MaintenanceStep]] = {}
    for step in maintenance_steps():
        bucket = index.get(step.group)
        if bucket is None:
            bucket = []
            index[step.group] = bucket
            groups.append((step.group, bucket))
        bucket.append(step)
    return groups
```

</details>

## 🔧 Function `maintenance_steps`

```python
def maintenance_steps() -> tuple[MaintenanceStep, ...]
```

Resolve and cache checklist steps.

<details>
<summary>Code:</summary>

```python
def maintenance_steps() -> tuple[MaintenanceStep, ...]:
    return tuple(_resolve_spec(spec) for spec in MAINTENANCE_STEP_SPECS)
```

</details>

## 🔧 Function `save_git_repos_all_clean`

```python
def save_git_repos_all_clean(*, all_clean: bool) -> None
```

Persist whether the last Git-repos check found every repo committed.

<details>
<summary>Code:</summary>

```python
def save_git_repos_all_clean(*, all_clean: bool) -> None:
    h.dev.config_update_value(_GIT_REPOS_ALL_CLEAN_KEY, bool(all_clean), get_config_path_str(), is_temp=True)
```

</details>

## 🔧 Function `save_py_check_all_passed`

```python
def save_py_check_all_passed(*, all_passed: bool) -> None
```

Persist whether the last Full PY check passed for every configured project.

<details>
<summary>Code:</summary>

```python
def save_py_check_all_passed(*, all_passed: bool) -> None:
    h.dev.config_update_value(_PY_CHECK_ALL_PASSED_KEY, bool(all_passed), get_config_path_str(), is_temp=True)
```

</details>

## 🔧 Function `save_show_update_hsk_step`

```python
def save_show_update_hsk_step(*, enabled: bool) -> None
```

Persist whether the Update HSK checklist row is visible (`config-temp.json`).

<details>
<summary>Code:</summary>

```python
def save_show_update_hsk_step(*, enabled: bool) -> None:
    h.dev.config_update_value(_SHOW_UPDATE_HSK_KEY, bool(enabled), get_config_path_str(), is_temp=True)
```

</details>
