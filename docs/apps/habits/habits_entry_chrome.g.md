---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habits_entry_chrome.py`

## 🔧 Function `install_habits_entry_chrome`

```python
def install_habits_entry_chrome(host: Any) -> None
```

Polish Habit form buttons, captions, and quiet GroupBoxes.

<details>
<summary>Code:</summary>

```python
def install_habits_entry_chrome(host: Any) -> None:
    _polish_form(host)
    if not getattr(host, "_habits_entry_theme_bound", False):
        bind_theme(host, lambda: _polish_form(host))
        host._habits_entry_theme_bound = True  # noqa: SLF001
```

</details>
