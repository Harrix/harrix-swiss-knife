---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tracker_splitter_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `clean_positive_ints`](#-function-clean_positive_ints)
- [🔧 Function `load_splitter_sizes`](#-function-load_splitter_sizes)
- [🔧 Function `save_splitter_sizes`](#-function-save_splitter_sizes)

</details>

## 🔧 Function `clean_positive_ints`

```python
def clean_positive_ints(raw: Sequence[object], *, expected_len: int, fallback: list[int]) -> list[int]
```

Return `expected_len` positive ints, or `fallback` when parsing fails.

<details>
<summary>Code:</summary>

```python
def clean_positive_ints(raw: Sequence[object], *, expected_len: int, fallback: list[int]) -> list[int]:
    cleaned: list[int] = []
    for item in raw:
        if isinstance(item, bool):
            return list(fallback)
        if isinstance(item, int):
            number = item
        elif isinstance(item, float):
            number = int(item)
        elif isinstance(item, str):
            try:
                number = int(item.strip())
            except ValueError:
                return list(fallback)
        else:
            return list(fallback)
        if number <= 0:
            return list(fallback)
        cleaned.append(number)
    if len(cleaned) != expected_len:
        return list(fallback)
    return cleaned
```

</details>

## 🔧 Function `load_splitter_sizes`

```python
def load_splitter_sizes(key: str, default: Sequence[int]) -> list[int]
```

Return persisted positive splitter sizes for `key`, or `default`.

<details>
<summary>Code:</summary>

```python
def load_splitter_sizes(key: str, default: Sequence[int]) -> list[int]:
    fallback = list(default)
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return fallback
    raw = config.get(key)
    if not isinstance(raw, list):
        return fallback
    return clean_positive_ints(raw, expected_len=len(fallback), fallback=fallback)
```

</details>

## 🔧 Function `save_splitter_sizes`

```python
def save_splitter_sizes(key: str, sizes: Sequence[int], default: Sequence[int]) -> list[int]
```

Persist positive splitter sizes for `key`.

<details>
<summary>Code:</summary>

```python
def save_splitter_sizes(key: str, sizes: Sequence[int], default: Sequence[int]) -> list[int]:
    fallback = list(default)
    cleaned = clean_positive_ints(sizes, expected_len=len(fallback), fallback=fallback)
    _ensure_temp_config()
    h.dev.config_update_value(key, cleaned, get_config_path_str(), is_temp=True)
    return cleaned
```

</details>
