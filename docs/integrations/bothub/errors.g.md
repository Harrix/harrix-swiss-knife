---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `errors.py`

## 🔧 Function `show_bothub_prompt_build_error`

```python
def show_bothub_prompt_build_error(parent: QWidget | None, exc: ValueError) -> None
```

Show a dialog for prompt-build failures from BotHub integrations.

<details>
<summary>Code:</summary>

```python
def show_bothub_prompt_build_error(parent: QWidget | None, exc: ValueError) -> None:
    msg = str(exc)
    if msg == API_KEY_MISSING_MSG:
        message_box.warning(parent, "BotHub API Key", msg)
    elif msg == PROMPT_MISSING_MSG:
        message_box.warning(parent, "Prompt", msg)
    else:
        message_box.warning(parent, "Prompt", msg)
```

</details>
