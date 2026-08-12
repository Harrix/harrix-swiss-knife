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
- [🔧 Function `load_category_icons`](#-function-load_category_icons)
- [🔧 Function `load_icon_size`](#-function-load_icon_size)
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
