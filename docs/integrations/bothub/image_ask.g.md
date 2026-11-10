---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_ask.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_image_ask_prompt`](#-function-build_image_ask_prompt)
- [🔧 Function `get_image_ask_prompt_template`](#-function-get_image_ask_prompt_template)

</details>

## 🔧 Function `build_image_ask_prompt`

```python
def build_image_ask_prompt(config: dict[str, Any], note: str = '') -> str
```

Build BotHub prompt that answers a question about a screenshot.

Raises:

- `ValueError`: If prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_image_ask_prompt(config: dict[str, Any], note: str = "") -> str:
    note_text = note.strip() or _EMPTY_NOTE
    return build_prompt(
        config,
        "image_ask",
        {"NOTE": note_text},
        prompt_display_name="image_ask",
    )
```

</details>

## 🔧 Function `get_image_ask_prompt_template`

```python
def get_image_ask_prompt_template(config: dict[str, Any]) -> str | None
```

Return stripped `prompts.image_ask` template, or `None` if missing.

<details>
<summary>Code:</summary>

```python
def get_image_ask_prompt_template(config: dict[str, Any]) -> str | None:
    return get_prompt_template(config, "image_ask")
```

</details>
