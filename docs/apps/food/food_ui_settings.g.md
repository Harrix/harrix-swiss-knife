---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_ui_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_column_visibility`](#-function-load_column_visibility)
- [🔧 Function `load_food_splitter_sizes`](#-function-load_food_splitter_sizes)
- [🔧 Function `save_column_visibility`](#-function-save_column_visibility)
- [🔧 Function `save_food_splitter_sizes`](#-function-save_food_splitter_sizes)

</details>

## 🔧 Function `load_column_visibility`

```python
def load_column_visibility() -> dict[str, bool]
```

Return persisted food-log column/header visibility flags merged with defaults.

<details>
<summary>Code:</summary>

```python
def load_column_visibility() -> dict[str, bool]:
    flags = dict(DEFAULT_COLUMN_VISIBILITY)
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return flags
    raw = config.get(COLUMN_VISIBILITY_KEY)
    if not isinstance(raw, dict):
        return flags
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, bool) and key in flags:
            flags[key] = value
    return flags
```

</details>

## 🔧 Function `load_food_splitter_sizes`

```python
def load_food_splitter_sizes() -> list[int]
```

Return Food-tab splitter sizes (form, items, log).

<details>
<summary>Code:</summary>

```python
def load_food_splitter_sizes() -> list[int]:
    return load_splitter_sizes(FOOD_SPLITTER_SIZES_KEY, FOOD_SPLITTER_SIZES_DEFAULT)
```

</details>

## 🔧 Function `save_column_visibility`

```python
def save_column_visibility(flags: dict[str, bool]) -> dict[str, bool]
```

Persist food-log column/header visibility flags.

<details>
<summary>Code:</summary>

```python
def save_column_visibility(flags: dict[str, bool]) -> dict[str, bool]:
    cleaned = {key: bool(value) for key, value in flags.items() if isinstance(key, str)}
    merged = dict(DEFAULT_COLUMN_VISIBILITY)
    merged.update(cleaned)
    _ensure_temp_config()
    h.dev.config_update_value(
        COLUMN_VISIBILITY_KEY,
        merged,
        get_config_path_str(),
        is_temp=True,
    )
    return merged
```

</details>

## 🔧 Function `save_food_splitter_sizes`

```python
def save_food_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Food-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_food_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    return save_splitter_sizes(FOOD_SPLITTER_SIZES_KEY, sizes, FOOD_SPLITTER_SIZES_DEFAULT)
```

</details>
