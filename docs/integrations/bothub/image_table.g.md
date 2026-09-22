---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_table.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_image_table_prompt`](#-function-build_image_table_prompt)
- [🔧 Function `get_image_table_model`](#-function-get_image_table_model)
- [🔧 Function `get_image_table_prompt_template`](#-function-get_image_table_prompt_template)

</details>

## 🔧 Function `build_image_table_prompt`

```python
def build_image_table_prompt(config: dict[str, Any]) -> str
```

Build BotHub prompt for extracting a styled table from an image.

Raises:

- `ValueError`: If the API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_image_table_prompt(config: dict[str, Any]) -> str:
    if get_prompt_template(config, PROMPT_KEY):
        return build_prompt(config, PROMPT_KEY, {}, prompt_display_name=PROMPT_KEY)
    ai_cfg = get_ai_section(config)
    return build_prompt(
        {**config, "ai": {**ai_cfg, "prompts": {**get_ai_prompts(config), PROMPT_KEY: _DEFAULT_PROMPT}}},
        PROMPT_KEY,
        {},
        prompt_display_name=PROMPT_KEY,
    )
```

</details>

## 🔧 Function `get_image_table_model`

```python
def get_image_table_model(config: dict[str, Any]) -> str
```

Return the chat model for table extraction (`ai.image_table_model`, else GPT-5.6).

<details>
<summary>Code:</summary>

```python
def get_image_table_model(config: dict[str, Any]) -> str:
    ai_cfg = get_ai_section(config)
    model = DEFAULT_IMAGE_TABLE_MODEL
    raw = str(ai_cfg.get(IMAGE_TABLE_MODEL_KEY) or "").strip()
    if raw:
        model = raw
    if get_chat_provider(config) == "openrouter" and "/" not in model:
        return f"openai/{model}"
    return model
```

</details>

## 🔧 Function `get_image_table_prompt_template`

```python
def get_image_table_prompt_template(config: dict[str, Any]) -> str
```

Return stripped `prompts.image_table_to_excel` template, or the built-in default.

<details>
<summary>Code:</summary>

```python
def get_image_table_prompt_template(config: dict[str, Any]) -> str:
    return get_prompt_template(config, PROMPT_KEY) or _DEFAULT_PROMPT.strip()
```

</details>
