---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_translate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_text_translate_prompt`](#-function-build_text_translate_prompt)
- [🔧 Function `get_text_translate_prompt_template`](#-function-get_text_translate_prompt_template)

</details>

## 🔧 Function `build_text_translate_prompt`

```python
def build_text_translate_prompt(text: str, config: dict[str, Any]) -> str
```

Build BotHub prompt to translate `text` into the local language.

Raises:

- `ValueError`: If prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_text_translate_prompt(text: str, config: dict[str, Any]) -> str:
    return build_prompt(
        config,
        "text_translate_to_local",
        {
            "TEXT": text,
            "LOCAL_LANGUAGE": get_apps_local_language_display_name(config),
            "LOCAL_LANGUAGE_CODE": get_apps_local_language(config),
        },
        prompt_display_name="text_translate_to_local",
    )
```

</details>

## 🔧 Function `get_text_translate_prompt_template`

```python
def get_text_translate_prompt_template(config: dict[str, Any]) -> str | None
```

Return stripped `prompts.text_translate_to_local` template, or `None` if missing.

<details>
<summary>Code:</summary>

```python
def get_text_translate_prompt_template(config: dict[str, Any]) -> str | None:
    return get_prompt_template(config, "text_translate_to_local")
```

</details>
