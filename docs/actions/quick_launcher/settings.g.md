---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `settings.py`

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
