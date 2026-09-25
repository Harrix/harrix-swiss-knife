---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tool_colors.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_tool_colors`](#-function-load_tool_colors)
- [🔧 Function `save_tool_colors`](#-function-save_tool_colors)

</details>

## 🔧 Function `load_tool_colors`

```python
def load_tool_colors(text_color: str) -> dict[str, str]
```

Load each drawing tool's last color, falling back to defaults.

`text_color` fills the text tool when `config-temp.json` has no saved text color.

<details>
<summary>Code:</summary>

```python
def load_tool_colors(text_color: str) -> dict[str, str]:
    colors = _default_tool_colors(text_color)
    try:
        loaded = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return colors
    if not isinstance(loaded, dict):
        return colors
    raw = loaded.get(_CONFIG_KEY)
    if not isinstance(raw, dict):
        return colors
    entry: dict[str, Any] = raw
    for key in _COLOR_TOOL_VALUES:
        parsed = _normalize_color(str(entry.get(key) or ""))
        if parsed:
            colors[key] = parsed
    return colors
```

</details>

## 🔧 Function `save_tool_colors`

```python
def save_tool_colors(colors: dict[str, str]) -> None
```

Persist each drawing tool's color into `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def save_tool_colors(colors: dict[str, str]) -> None:
    payload: dict[str, str] = {}
    for key in _COLOR_TOOL_VALUES:
        parsed = _normalize_color(str(colors.get(key) or ""))
        if parsed:
            payload[key] = parsed
    try:
        h.dev.config_update_value(_CONFIG_KEY, payload, get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return
```

</details>
