---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_fix.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_text_fix_prompt`](#-function-build_text_fix_prompt)
- [🔧 Function `fix_text_sync`](#-function-fix_text_sync)
- [🔧 Function `get_text_fix_prompt_template`](#-function-get_text_fix_prompt_template)

</details>

## 🔧 Function `build_text_fix_prompt`

```python
def build_text_fix_prompt(input_text: str, config: dict[str, Any]) -> str
```

Build full BotHub prompt for the given input text.

Raises:
ValueError: If prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_text_fix_prompt(input_text: str, config: dict[str, Any]) -> str:
    return build_prompt(config, "text_fix_ru", {"TEXT": input_text}, prompt_display_name="text_fix_ru")
```

</details>

## 🔧 Function `fix_text_sync`

```python
def fix_text_sync(input_text: str, config: dict[str, Any]) -> str
```

Send text to BotHub synchronously and return corrected text.

Raises:
ValueError: Configuration errors (prompt or API key).
BotHubApiError: API or network failure.

<details>
<summary>Code:</summary>

```python
def fix_text_sync(input_text: str, config: dict[str, Any]) -> str:
    prompt_text = build_text_fix_prompt(input_text, config)
    api_key, base_url, model, proxy_url = get_connection_params(config)
    return chat_completion(
        api_key=api_key,
        base_url=base_url,
        model=model,
        text=prompt_text,
        proxy_url=proxy_url,
    )
```

</details>

## 🔧 Function `get_text_fix_prompt_template`

```python
def get_text_fix_prompt_template(config: dict[str, Any]) -> str | None
```

Return stripped `prompts.text_fix_ru` template, or None if missing.

<details>
<summary>Code:</summary>

```python
def get_text_fix_prompt_template(config: dict[str, Any]) -> str | None:
    return get_prompt_template(config, "text_fix_ru")
```

</details>
