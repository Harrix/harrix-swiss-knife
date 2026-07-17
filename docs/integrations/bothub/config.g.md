---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_connection_params`](#-function-get_connection_params)
- [🔧 Function `get_speech_model`](#-function-get_speech_model)
- [🔧 Function `validate_api_key`](#-function-validate_api_key)

</details>

## 🔧 Function `get_connection_params`

```python
def get_connection_params(config: dict[str, Any]) -> tuple[str, str, str, str | None]
```

Return (api_key, base_url, model, proxy_url) for BotHub chat completion.

<details>
<summary>Code:</summary>

```python
def get_connection_params(config: dict[str, Any]) -> tuple[str, str, str, str | None]:
    api_key = str(config.get("bothub_api_key", "")).strip()
    bothub_cfg = config.get("bothub") or {}
    base_url = str(bothub_cfg.get("base_url", "https://bothub.chat/api/v2/openai/v1")).strip()
    model = str(bothub_cfg.get("model", "gpt-5.4")).strip()
    proxy_url = resolve_bothub_proxy_url(config)
    return api_key, base_url, model, proxy_url
```

</details>

## 🔧 Function `get_speech_model`

```python
def get_speech_model(config: dict[str, Any]) -> str
```

Return speech recognition model ID from config.

<details>
<summary>Code:</summary>

```python
def get_speech_model(config: dict[str, Any]) -> str:
    bothub_cfg = config.get("bothub") or {}
    return str(bothub_cfg.get("speech_model", "gemini-3.1-flash-lite-preview")).strip()
```

</details>

## 🔧 Function `validate_api_key`

```python
def validate_api_key(config: dict[str, Any]) -> str | None
```

Return API key if configured; optionally show warning dialog and return None.

<details>
<summary>Code:</summary>

```python
def validate_api_key(
    config: dict[str, Any],
    *,
    parent: QWidget | None = None,
    show_message: bool = True,
) -> str | None:
    api_key = str(config.get("bothub_api_key", "")).strip()
    if api_key and not api_key.startswith("paste-your-"):
        return api_key
    if show_message:
        message_box.warning(parent, "BotHub API Key", API_KEY_MISSING_MSG)
    return None
```

</details>
