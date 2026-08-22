---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `API_KEY_MISSING_MSG`](#-constant-api_key_missing_msg)
- [🔧 Function `get_active_provider`](#-function-get_active_provider)
- [🔧 Function `get_connection_params`](#-function-get_connection_params)
- [🔧 Function `get_proxy_url`](#-function-get_proxy_url)
- [🔧 Function `get_speech_model`](#-function-get_speech_model)
- [🔧 Function `validate_api_key`](#-function-validate_api_key)

</details>

## 📎 Constant `API_KEY_MISSING_MSG`

```python
API_KEY_MISSING_MSG = 'AI API key is not configured.\n\nSet ai.provider in config.json and add the matching key file under api-keys/.'
```

_No docstring provided._

## 🔧 Function `get_active_provider`

```python
def get_active_provider(config: dict[str, Any], *, for_speech: bool = False) -> ProviderName
```

Return chat or speech provider ID from config.

<details>
<summary>Code:</summary>

```python
def get_active_provider(config: dict[str, Any], *, for_speech: bool = False) -> ProviderName:
    return get_speech_provider(config) if for_speech else get_chat_provider(config)
```

</details>

## 🔧 Function `get_connection_params`

```python
def get_connection_params(config: dict[str, Any], *, for_speech: bool = False) -> tuple[str, str, str, str | None]
```

Return `(api_key, base_url, model, proxy_url)` for the active provider.

<details>
<summary>Code:</summary>

```python
def get_connection_params(
    config: dict[str, Any],
    *,
    for_speech: bool = False,
) -> tuple[str, str, str, str | None]:
    provider = get_active_provider(config, for_speech=for_speech)
    api_key, base_url, model, _ = get_connection_params_for_provider(
        config,
        provider,
        for_speech=for_speech,
    )
    return api_key, base_url, model, resolve_bothub_proxy_url(config)
```

</details>

## 🔧 Function `get_proxy_url`

```python
def get_proxy_url(config: dict[str, Any]) -> str | None
```

Resolve HTTP proxy for AI requests.

<details>
<summary>Code:</summary>

```python
def get_proxy_url(config: dict[str, Any]) -> str | None:
    return resolve_bothub_proxy_url(config)
```

</details>

## 🔧 Function `get_speech_model`

```python
def get_speech_model(config: dict[str, Any]) -> str
```

Return speech recognition model ID from the speech provider settings.

<details>
<summary>Code:</summary>

```python
def get_speech_model(config: dict[str, Any]) -> str:
    provider = get_speech_provider(config)
    return get_speech_model_for_provider(config, provider)
```

</details>

## 🔧 Function `validate_api_key`

```python
def validate_api_key(config: dict[str, Any], *, parent: QWidget | None = None, show_message: bool = True, for_speech: bool = False) -> str | None
```

Return API key if configured; optionally show warning dialog and return `None`.

<details>
<summary>Code:</summary>

```python
def validate_api_key(
    config: dict[str, Any],
    *,
    parent: QWidget | None = None,
    show_message: bool = True,
    for_speech: bool = False,
) -> str | None:
    provider = get_active_provider(config, for_speech=for_speech)
    if for_speech and not provider_supports_speech(provider):
        if show_message:
            message_box.warning(
                parent,
                "AI Speech",
                (
                    "Anthropic does not support speech-to-text.\n\n"
                    'Set ai.speech_provider to "openai", "gemini", "bothub", or "bothub.ru".'
                ),
            )
        return None

    api_key = get_api_key(config, provider)
    if api_key and not api_key.startswith("paste-your-"):
        return api_key
    if show_message:
        message_box.warning(parent, "AI API Key", get_api_key_missing_message(provider))
    return None
```

</details>
