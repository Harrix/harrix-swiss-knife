---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_rewrite.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_text_rewrite_prompt`](#-function-build_text_rewrite_prompt)
- [🔧 Function `get_text_rewrite_prompt_template`](#-function-get_text_rewrite_prompt_template)
- [🔧 Function `rewrite_text_sync`](#-function-rewrite_text_sync)

</details>

## 🔧 Function `build_text_rewrite_prompt`

```python
def build_text_rewrite_prompt(input_text: str, config: dict[str, Any]) -> str
```

Build full BotHub prompt for deep text rewrite.

Raises:

- `ValueError`: If prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_text_rewrite_prompt(input_text: str, config: dict[str, Any]) -> str:
    return build_prompt(config, "text_rewrite_ru", {"TEXT": input_text}, prompt_display_name="text_rewrite_ru")
```

</details>

## 🔧 Function `get_text_rewrite_prompt_template`

```python
def get_text_rewrite_prompt_template(config: dict[str, Any]) -> str | None
```

Return stripped `prompts.text_rewrite_ru` template, or None if missing.

<details>
<summary>Code:</summary>

```python
def get_text_rewrite_prompt_template(config: dict[str, Any]) -> str | None:
    return get_prompt_template(config, "text_rewrite_ru")
```

</details>

## 🔧 Function `rewrite_text_sync`

```python
def rewrite_text_sync(input_text: str, config: dict[str, Any]) -> str
```

Send text to BotHub synchronously and return rewritten text.

Raises:

- `ValueError`: Configuration errors (prompt or API key).
- `BotHubApiError`: API or network failure.

<details>
<summary>Code:</summary>

```python
def rewrite_text_sync(input_text: str, config: dict[str, Any]) -> str:
    prompt_text = build_text_rewrite_prompt(input_text, config)
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
