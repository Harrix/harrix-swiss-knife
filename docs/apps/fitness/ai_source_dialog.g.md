---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ai_source_dialog.py`

## 🔧 Function `create_fitness_dashboard_text_dialog`

```python
def create_fitness_dashboard_text_dialog(parent: QWidget | None = None) -> TextImageSourceDialog
```

Build a text-only, large-type dialog for the Fitness dashboard.

<details>
<summary>Code:</summary>

```python
def create_fitness_dashboard_text_dialog(parent: QWidget | None = None) -> TextImageSourceDialog:
    return TextImageSourceDialog(
        parent,
        title="Write text",
        description="Describe the sets you completed. AI will turn this into a set list.",
        placeholder=SETS_TEXT_PLACEHOLDER,
        show_text=True,
        text_required=True,
        show_images=False,
        show_skip_manual=False,
        accept_button_text="Send to AI",
        accept_button_emoji="🤖",
        accept_button_style=SEND_TO_AI_BUTTON_STYLE,
        large_ui=True,
    )
```

</details>
