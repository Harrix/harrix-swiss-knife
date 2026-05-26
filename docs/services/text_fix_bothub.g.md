---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_fix_bothub.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_text_fix_prompt`](#-function-build_text_fix_prompt)
- [🔧 Function `fix_text_sync`](#-function-fix_text_sync)
- [🔧 Function `get_bothub_connection_params`](#-function-get_bothub_connection_params)
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
    template = get_text_fix_prompt_template(config)
    if not template:
        raise ValueError(PROMPT_MISSING_MSG)
    api_key, _, _, _ = get_bothub_connection_params(config)
    if not api_key:
        raise ValueError(API_KEY_MISSING_MSG)
    return template.replace("{{TEXT}}", input_text)
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
    api_key, base_url, model, proxy_url = get_bothub_connection_params(config)
    return chat_completion(
        api_key=api_key,
        base_url=base_url,
        model=model,
        text=prompt_text,
        proxy_url=proxy_url,
    )
```

</details>

## 🔧 Function `get_bothub_connection_params`

```python
def get_bothub_connection_params(config: dict[str, Any]) -> tuple[str, str, str, str | None]
```

Return (api_key, base_url, model, proxy_url) for BotHub chat completion.

<details>
<summary>Code:</summary>

```python
def get_bothub_connection_params(
    config: dict[str, Any],
) -> tuple[str, str, str, str | None]:
    api_key = str(config.get("bothub_api_key", "")).strip()
    bothub_cfg = config.get("bothub") or {}
    base_url = str(bothub_cfg.get("base_url", "https://bothub.chat/api/v2/openai/v1")).strip()
    model = str(bothub_cfg.get("model", "gpt-5.4")).strip()
    proxy_url = resolve_bothub_proxy_url(config)
    return api_key, base_url, model, proxy_url
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
    prompts_cfg = config.get("prompts") or {}
    template = str(prompts_cfg.get("text_fix_ru", "")).strip()
    return template or None
```

</details>
