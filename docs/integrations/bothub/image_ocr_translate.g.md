---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_ocr_translate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_image_ocr_translate_prompt`](#-function-build_image_ocr_translate_prompt)
- [🔧 Function `get_image_ocr_translate_prompt_template`](#-function-get_image_ocr_translate_prompt_template)

</details>

## 🔧 Function `build_image_ocr_translate_prompt`

```python
def build_image_ocr_translate_prompt(config: dict[str, Any]) -> str
```

Build BotHub prompt for image OCR with optional translation.

Raises:

- `ValueError`: If prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_image_ocr_translate_prompt(config: dict[str, Any]) -> str:
    return build_prompt(
        config,
        "image_ocr_translate",
        {
            "LOCAL_LANGUAGE": get_apps_local_language_display_name(config),
            "LOCAL_LANGUAGE_CODE": get_apps_local_language(config),
        },
        prompt_display_name="image_ocr_translate",
    )
```

</details>

## 🔧 Function `get_image_ocr_translate_prompt_template`

```python
def get_image_ocr_translate_prompt_template(config: dict[str, Any]) -> str | None
```

Return stripped `prompts.image_ocr_translate` template, or `None` if missing.

<details>
<summary>Code:</summary>

```python
def get_image_ocr_translate_prompt_template(config: dict[str, Any]) -> str | None:
    return get_prompt_template(config, "image_ocr_translate")
```

</details>
