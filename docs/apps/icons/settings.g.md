---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_favorites`](#-function-add_favorites)
- [🔧 Function `clamp_icon_size`](#-function-clamp_icon_size)
- [🔧 Function `clamp_recent_folders_max`](#-function-clamp_recent_folders_max)
- [🔧 Function `is_favorites_category`](#-function-is_favorites_category)
- [🔧 Function `load_category_icons`](#-function-load_category_icons)
- [🔧 Function `load_favorites`](#-function-load_favorites)
- [🔧 Function `load_favorites_map`](#-function-load_favorites_map)
- [🔧 Function `load_icon_size`](#-function-load_icon_size)
- [🔧 Function `load_last_folder`](#-function-load_last_folder)
- [🔧 Function `load_last_icon`](#-function-load_last_icon)
- [🔧 Function `load_last_icons`](#-function-load_last_icons)
- [🔧 Function `load_pinned_folders`](#-function-load_pinned_folders)
- [🔧 Function `load_recent_folders`](#-function-load_recent_folders)
- [🔧 Function `load_recent_folders_max`](#-function-load_recent_folders_max)
- [🔧 Function `pin_folder`](#-function-pin_folder)
- [🔧 Function `remember_recent_folder`](#-function-remember_recent_folder)
- [🔧 Function `remove_favorites`](#-function-remove_favorites)
- [🔧 Function `rename_favorite`](#-function-rename_favorite)
- [🔧 Function `save_category_icons`](#-function-save_category_icons)
- [🔧 Function `save_favorites`](#-function-save_favorites)
- [🔧 Function `save_icon_size`](#-function-save_icon_size)
- [🔧 Function `save_last_folder`](#-function-save_last_folder)
- [🔧 Function `save_last_icon`](#-function-save_last_icon)
- [🔧 Function `set_category_icon`](#-function-set_category_icon)
- [🔧 Function `sidebar_category_names`](#-function-sidebar_category_names)
- [🔧 Function `toggle_favorite`](#-function-toggle_favorite)

</details>

## 🔧 Function `add_favorites`

```python
def add_favorites(folder: Path, family_ids: list[str]) -> list[str]
```

Append `family_ids` to favorites for `folder`, keeping existing order.

<details>
<summary>Code:</summary>

```python
def add_favorites(folder: Path, family_ids: list[str]) -> list[str]:
    return save_favorites(folder, [*load_favorites(folder), *family_ids])
```

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

## 🔧 Function `is_favorites_category`

```python
def is_favorites_category(name: str | None) -> bool
```

Return whether `name` is the sidebar Favorites category.

<details>
<summary>Code:</summary>

```python
def is_favorites_category(name: str | None) -> bool:
    return bool(name) and name.casefold() == FAVORITES_CATEGORY.casefold()
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

## 🔧 Function `load_favorites`

```python
def load_favorites(folder: Path) -> list[str]
```

Return favorite family IDs for `folder`, oldest first.

<details>
<summary>Code:</summary>

```python
def load_favorites(folder: Path) -> list[str]:
    return load_favorites_map().get(_folder_key(folder), [])
```

</details>

## 🔧 Function `load_favorites_map`

```python
def load_favorites_map() -> dict[str, list[str]]
```

Load folder → favorite family-id lists from `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def load_favorites_map() -> dict[str, list[str]]:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return {}
    raw = config.get(FAVORITES_KEY)
    if not isinstance(raw, dict):
        return {}
    result: dict[str, list[str]] = {}
    for key, value in raw.items():
        folder = _normalize_folder_key(str(key))
        ids = _clean_family_ids(value)
        if folder and ids:
            result[folder] = ids
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

## 🔧 Function `load_last_folder`

```python
def load_last_folder() -> Path | None
```

Return the last opened icons folder, if stored and existing.

<details>
<summary>Code:</summary>

```python
def load_last_folder() -> Path | None:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return None
    raw = str(config.get(LAST_FOLDER_KEY) or "").strip()
    if not raw or raw.startswith("<"):
        return None
    path = Path(raw)
    if not path.is_dir():
        return None
    return path
```

</details>

## 🔧 Function `load_last_icon`

```python
def load_last_icon(folder: Path) -> str | None
```

Return the last selected family ID for `folder`, if stored.

<details>
<summary>Code:</summary>

```python
def load_last_icon(folder: Path) -> str | None:
    family_id = load_last_icons().get(_folder_key(folder), "").strip()
    return family_id or None
```

</details>

## 🔧 Function `load_last_icons`

```python
def load_last_icons() -> dict[str, str]
```

Load folder → last family-id map from `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def load_last_icons() -> dict[str, str]:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return {}
    raw = config.get(LAST_ICONS_KEY)
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for key, value in raw.items():
        folder = _normalize_folder_key(str(key))
        family_id = str(value).strip()
        if folder and family_id:
            result[folder] = family_id
    return result
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
        [_path_to_config_string(item) for item in updated],
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
        [_path_to_config_string(item) for item in updated],
        get_config_path_str(),
        is_temp=True,
    )
    return updated
```

</details>

## 🔧 Function `remove_favorites`

```python
def remove_favorites(folder: Path, family_ids: list[str]) -> list[str]
```

Remove `family_ids` from favorites for `folder`.

<details>
<summary>Code:</summary>

```python
def remove_favorites(folder: Path, family_ids: list[str]) -> list[str]:
    drop = {item.strip() for item in family_ids if item.strip()}
    return save_favorites(folder, [item for item in load_favorites(folder) if item not in drop])
```

</details>

## 🔧 Function `rename_favorite`

```python
def rename_favorite(folder: Path, old_family_id: str, new_family_id: str) -> list[str]
```

Replace `old_family_id` with `new_family_id` in favorites when present.

<details>
<summary>Code:</summary>

```python
def rename_favorite(folder: Path, old_family_id: str, new_family_id: str) -> list[str]:
    old_id = old_family_id.strip()
    new_id = new_family_id.strip()
    current = load_favorites(folder)
    if not old_id or old_id not in current:
        return current
    updated: list[str] = []
    seen: set[str] = set()
    for item in current:
        replacement = new_id if item == old_id else item
        if not replacement or replacement in seen:
            continue
        seen.add(replacement)
        updated.append(replacement)
    return save_favorites(folder, updated)
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

## 🔧 Function `save_favorites`

```python
def save_favorites(folder: Path, family_ids: list[str]) -> list[str]
```

Persist favorite family IDs for `folder` in `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def save_favorites(folder: Path, family_ids: list[str]) -> list[str]:
    cleaned = _clean_family_ids(family_ids)
    mapping = load_favorites_map()
    key = _folder_key(folder)
    if cleaned:
        mapping[key] = cleaned
    else:
        mapping.pop(key, None)
    _ensure_temp_config()
    h.dev.config_update_value(
        FAVORITES_KEY,
        mapping,
        get_config_path_str(),
        is_temp=True,
    )
    return cleaned
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

## 🔧 Function `save_last_folder`

```python
def save_last_folder(folder: Path) -> None
```

Remember the last opened icons folder in `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def save_last_folder(folder: Path) -> None:
    resolved = folder.expanduser().resolve()
    if not resolved.is_dir():
        return
    _ensure_temp_config()
    h.dev.config_update_value(
        LAST_FOLDER_KEY,
        _path_to_config_string(resolved),
        get_config_path_str(),
        is_temp=True,
    )
```

</details>

## 🔧 Function `save_last_icon`

```python
def save_last_icon(folder: Path, family_id: str) -> None
```

Remember `family_id` as the last selected icon in `folder`.

<details>
<summary>Code:</summary>

```python
def save_last_icon(folder: Path, family_id: str) -> None:
    cleaned_id = family_id.strip()
    if not cleaned_id:
        return
    mapping = load_last_icons()
    mapping[_folder_key(folder)] = cleaned_id
    _ensure_temp_config()
    h.dev.config_update_value(
        LAST_ICONS_KEY,
        mapping,
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

## 🔧 Function `sidebar_category_names`

```python
def sidebar_category_names(catalog_names: list[str], *, has_favorites: bool = False) -> list[str]
```

Return sidebar categories with Favorites first when it has icons.

<details>
<summary>Code:</summary>

```python
def sidebar_category_names(catalog_names: list[str], *, has_favorites: bool = False) -> list[str]:
    rest = [name for name in catalog_names if not is_favorites_category(name)]
    if has_favorites:
        return [FAVORITES_CATEGORY, *rest]
    return rest
```

</details>

## 🔧 Function `toggle_favorite`

```python
def toggle_favorite(folder: Path, family_id: str) -> tuple[list[str], bool]
```

Add or remove `family_id` in favorites for `folder`.

Returns:

- The updated favorite IDs
- `True` when the icon was added, `False` when it was removed

<details>
<summary>Code:</summary>

```python
def toggle_favorite(folder: Path, family_id: str) -> tuple[list[str], bool]:
    cleaned = family_id.strip()
    current = load_favorites(folder)
    if cleaned in current:
        return save_favorites(folder, [item for item in current if item != cleaned]), False
    return save_favorites(folder, [*current, cleaned]), True
```

</details>
