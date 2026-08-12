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
- [🔧 Function `load_icon_size`](#-function-load_icon_size)
- [🔧 Function `save_icon_size`](#-function-save_icon_size)

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

## 🔧 Function `save_icon_size`

```python
def save_icon_size(size: int) -> None
```

Persist icon display size in `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def save_icon_size(size: int) -> None:
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")
    h.dev.config_update_value(
        ICON_SIZE_KEY,
        clamp_icon_size(size),
        get_config_path_str(),
        is_temp=True,
    )
```

</details>
