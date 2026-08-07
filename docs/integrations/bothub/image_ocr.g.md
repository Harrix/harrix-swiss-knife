---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_ocr.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_image_ocr_prompt`](#-function-build_image_ocr_prompt)
- [🔧 Function `get_image_ocr_prompt_template`](#-function-get_image_ocr_prompt_template)

</details>

## 🔧 Function `build_image_ocr_prompt`

```python
def build_image_ocr_prompt(config: dict[str, Any]) -> str
```

Build BotHub prompt for image OCR.

Raises:

- `ValueError`: If prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_image_ocr_prompt(config: dict[str, Any]) -> str:
    return build_prompt(
        config,
        "image_ocr_to_markdown",
        {},
        prompt_display_name="image_ocr_to_markdown",
    )
```

</details>

## 🔧 Function `get_image_ocr_prompt_template`

```python
def get_image_ocr_prompt_template(config: dict[str, Any]) -> str | None
```

Return stripped `prompts.image_ocr_to_markdown` template, or `None` if missing.

<details>
<summary>Code:</summary>

```python
def get_image_ocr_prompt_template(config: dict[str, Any]) -> str | None:
    return get_prompt_template(config, "image_ocr_to_markdown")
```

</details>
