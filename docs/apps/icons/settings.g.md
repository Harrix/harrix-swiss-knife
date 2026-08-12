---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `clamp_icon_size`](#-function-clamp_icon_size)
- [🔧 Function `clamp_recent_folders_max`](#-function-clamp_recent_folders_max)
- [🔧 Function `load_category_icons`](#-function-load_category_icons)
- [🔧 Function `load_icon_size`](#-function-load_icon_size)
- [🔧 Function `load_pinned_folders`](#-function-load_pinned_folders)
- [🔧 Function `load_recent_folders`](#-function-load_recent_folders)
- [🔧 Function `load_recent_folders_max`](#-function-load_recent_folders_max)
- [🔧 Function `pin_folder`](#-function-pin_folder)
- [🔧 Function `remember_recent_folder`](#-function-remember_recent_folder)
- [🔧 Function `save_category_icons`](#-function-save_category_icons)
- [🔧 Function `save_icon_size`](#-function-save_icon_size)
- [🔧 Function `set_category_icon`](#-function-set_category_icon)

</details>

## 🔧 Function `clamp_icon_size`

```python
def clamp_icon_size(value: object) -> int
```

Return icon size clamped to the supported slider range.

<details>
<summary>Code:</summary>

```python
def clamp_icon_size(value: object) -> int:
    if isinstance(value, bool):
        return ICON_SIZE_DEFAULT
    if isinstance(value, int):
        size = value
    elif isinstance(value, float):
        size = int(value)
    elif isinstance(value, str):
        try:
            size = int(value.strip())
        except ValueError:
            return ICON_SIZE_DEFAULT
    else:
        return ICON_SIZE_DEFAULT
    return max(ICON_SIZE_MIN, min(ICON_SIZE_MAX, size))
```

</details>

## 🔧 Function `clamp_recent_folders_max`

```python
def clamp_recent_folders_max(value: object) -> int
```

Return recent-folders capacity clamped to a safe range.

<details>
<summary>Code:</summary>

```python
def clamp_recent_folders_max(value: object) -> int:
    if isinstance(value, bool):
        return RECENT_FOLDERS_MAX_DEFAULT
    if isinstance(value, int):
        size = value
    elif isinstance(value, float):
        size = int(value)
    elif isinstance(value, str):
        try:
            size = int(value.strip())
        except ValueError:
            return RECENT_FOLDERS_MAX_DEFAULT
    else:
        return RECENT_FOLDERS_MAX_DEFAULT
    return max(1, min(RECENT_FOLDERS_MAX_LIMIT, size))
```

</details>

## 🔧 Function `load_category_icons`

```python
def load_category_icons() -> dict[str, str]
```

Load category → family-id map from `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def load_category_icons() -> dict[str, str]:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return {}
    raw = config.get(CATEGORY_ICONS_KEY)
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for key, value in raw.items():
        category = str(key).strip()
        family_id = str(value).strip()
        if category and family_id:
            result[category] = family_id
    return result
```

</details>

## 🔧 Function `load_icon_size`

```python
def load_icon_size() -> int
```

Load icon display size from `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def load_icon_size() -> int:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return ICON_SIZE_DEFAULT
    return clamp_icon_size(config.get(ICON_SIZE_KEY, ICON_SIZE_DEFAULT))
```

</details>

## 🔧 Function `load_pinned_folders`

```python
def load_pinned_folders() -> list[Path]
```

Load pinned folders from `config.json` (`path_vector_icons_pinned`).

When the pinned list is empty, fall back to `path_vector_icons` and
`path_vector_icons_ai` when those paths exist.

<details>
<summary>Code:</summary>

```python
def load_pinned_folders() -> list[Path]:
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return []
    pinned = _parse_path_list(config.get(PINNED_FOLDERS_KEY))
    if pinned:
        return pinned
    fallback: list[Path] = []
    for key in ("path_vector_icons", "path_vector_icons_ai"):
        raw = str(config.get(key) or "").strip()
        if not raw or raw.startswith("<"):
            continue
        path = Path(raw)
        if path.is_dir() and path not in fallback:
            fallback.append(path)
    return fallback
```

</details>

## 🔧 Function `load_recent_folders`

```python
def load_recent_folders() -> list[Path]
```

Load recent folders from `config-temp.json`, newest first.

<details>
<summary>Code:</summary>

```python
def load_recent_folders() -> list[Path]:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return []
    paths = _parse_path_list(config.get(RECENT_FOLDERS_KEY))
    return paths[: load_recent_folders_max()]
```

</details>

## 🔧 Function `load_recent_folders_max`

```python
def load_recent_folders_max() -> int
```

Load max unique recent folders from `config.json`.

<details>
<summary>Code:</summary>

```python
def load_recent_folders_max() -> int:
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return RECENT_FOLDERS_MAX_DEFAULT
    return clamp_recent_folders_max(config.get(RECENT_FOLDERS_MAX_KEY, RECENT_FOLDERS_MAX_DEFAULT))
```

</details>

## 🔧 Function `pin_folder`

```python
def pin_folder(path: Path) -> list[Path]
```

Add `path` to pinned folders in `config.json` and return the new list.

<details>
<summary>Code:</summary>

```python
def pin_folder(path: Path) -> list[Path]:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        return load_pinned_folders()
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        config = {}
    existing = _parse_path_list(config.get(PINNED_FOLDERS_KEY))
    if not existing:
        # Materialize fallback defaults before appending.
        existing = load_pinned_folders()
    updated = [resolved, *[item for item in existing if item.resolve() != resolved]]
    h.dev.config_update_value(
        PINNED_FOLDERS_KEY,
        [str(item) for item in updated],
        get_config_path_str(),
    )
    return updated
```

</details>

## 🔧 Function `remember_recent_folder`

```python
def remember_recent_folder(path: Path) -> list[Path]
```

Prepend `path` to recent folders and persist in `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def remember_recent_folder(path: Path) -> list[Path]:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        return load_recent_folders()
    max_count = load_recent_folders_max()
    current = [item for item in load_recent_folders() if item.resolve() != resolved]
    updated = [resolved, *current][:max_count]
    _ensure_temp_config()
    h.dev.config_update_value(
        RECENT_FOLDERS_KEY,
        [str(item) for item in updated],
        get_config_path_str(),
        is_temp=True,
    )
    return updated
```

</details>

## 🔧 Function `save_category_icons`

```python
def save_category_icons(mapping: dict[str, str]) -> None
```

Persist category → family-id map in `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def save_category_icons(mapping: dict[str, str]) -> None:
    cleaned: dict[str, str] = {}
    for key, value in mapping.items():
        category = str(key).strip()
        family_id = str(value).strip()
        if category and family_id:
            cleaned[category] = family_id
    _ensure_temp_config()
    h.dev.config_update_value(
        CATEGORY_ICONS_KEY,
        cleaned,
        get_config_path_str(),
        is_temp=True,
    )
```

</details>

## 🔧 Function `save_icon_size`

```python
def save_icon_size(size: int) -> None
```

Persist icon display size in `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def save_icon_size(size: int) -> None:
    _ensure_temp_config()
    h.dev.config_update_value(
        ICON_SIZE_KEY,
        clamp_icon_size(size),
        get_config_path_str(),
        is_temp=True,
    )
```

</details>

## 🔧 Function `set_category_icon`

```python
def set_category_icon(category: str, family_id: str) -> dict[str, str]
```

Assign `family_id` as the icon for `category` and persist the map.

<details>
<summary>Code:</summary>

```python
def set_category_icon(category: str, family_id: str) -> dict[str, str]:
    mapping = load_category_icons()
    mapping[category.strip()] = family_id.strip()
    save_category_icons(mapping)
    return mapping
```

</details>
