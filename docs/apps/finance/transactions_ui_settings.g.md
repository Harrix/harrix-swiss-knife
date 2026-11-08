---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transactions_ui_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_column_visibility`](#-function-load_column_visibility)
- [🔧 Function `load_splitter_sizes`](#-function-load_splitter_sizes)
- [🔧 Function `save_column_visibility`](#-function-save_column_visibility)
- [🔧 Function `save_splitter_sizes`](#-function-save_splitter_sizes)

</details>

## 🔧 Function `load_column_visibility`

```python
def load_column_visibility() -> dict[str, bool]
```

Return persisted column/header visibility flags.

<details>
<summary>Code:</summary>

```python
def load_column_visibility() -> dict[str, bool]:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return {}
    raw = config.get(COLUMN_VISIBILITY_KEY)
    if not isinstance(raw, dict):
        return {}
    return {key: value for key, value in raw.items() if isinstance(key, str) and isinstance(value, bool)}
```

</details>

## 🔧 Function `load_splitter_sizes`

```python
def load_splitter_sizes() -> list[int]
```

Return Transactions-tab splitter sizes (form, categories, table).

<details>
<summary>Code:</summary>

```python
def load_splitter_sizes() -> list[int]:
    return _load_int_list(SPLITTER_SIZES_KEY, list(SPLITTER_SIZES_DEFAULT), expected_len=EXPECTED_SPLITTER_LEN)
```

</details>

## 🔧 Function `save_column_visibility`

```python
def save_column_visibility(flags: dict[str, bool]) -> dict[str, bool]
```

Persist column/header visibility flags.

<details>
<summary>Code:</summary>

```python
def save_column_visibility(flags: dict[str, bool]) -> dict[str, bool]:
    cleaned = {key: bool(value) for key, value in flags.items() if isinstance(key, str)}
    _ensure_temp_config()
    h.dev.config_update_value(
        COLUMN_VISIBILITY_KEY,
        cleaned,
        get_config_path_str(),
        is_temp=True,
    )
    return cleaned
```

</details>

## 🔧 Function `save_splitter_sizes`

```python
def save_splitter_sizes(sizes: Sequence[int]) -> list[int]
```

Persist Transactions-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def save_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    cleaned = _clean_positive_ints(sizes, expected_len=EXPECTED_SPLITTER_LEN, fallback=list(SPLITTER_SIZES_DEFAULT))
    _ensure_temp_config()
    h.dev.config_update_value(
        SPLITTER_SIZES_KEY,
        cleaned,
        get_config_path_str(),
        is_temp=True,
    )
    return cleaned
```

</details>
