---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `quick_launcher_settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY`](#-constant-quick_launcher_markdown_in_panel_key)
- [🔧 Function `load_quick_launcher_markdown_in_panel`](#-function-load_quick_launcher_markdown_in_panel)

</details>

## 📎 Constant `QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY`

```python
QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY = 'quick_launcher_markdown_in_panel'
```

_No docstring provided._

## 🔧 Function `load_quick_launcher_markdown_in_panel`

```python
def load_quick_launcher_markdown_in_panel() -> bool
```

Return whether Markdown commands appear in a separate quick launcher panel.

<details>
<summary>Code:</summary>

```python
def load_quick_launcher_markdown_in_panel() -> bool:
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return True
    value = config.get(QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY, True)
    if isinstance(value, bool):
        return value
    return bool(value)
```

</details>
