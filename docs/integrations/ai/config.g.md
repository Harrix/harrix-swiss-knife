---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_api_key`](#-function-get_api_key)
- [🔧 Function `get_api_key_missing_message`](#-function-get_api_key_missing_message)
- [🔧 Function `get_chat_provider`](#-function-get_chat_provider)
- [🔧 Function `get_connection_params_for_provider`](#-function-get_connection_params_for_provider)
- [🔧 Function `get_max_image_side`](#-function-get_max_image_side)
- [🔧 Function `get_provider_settings`](#-function-get_provider_settings)
- [🔧 Function `get_speech_model_for_provider`](#-function-get_speech_model_for_provider)
- [🔧 Function `get_speech_provider`](#-function-get_speech_provider)
- [🔧 Function `is_bothub_router`](#-function-is_bothub_router)
- [🔧 Function `normalize_provider`](#-function-normalize_provider)
- [🔧 Function `other_bothub_router`](#-function-other_bothub_router)
- [🔧 Function `provider_supports_speech`](#-function-provider_supports_speech)

</details>

## 🔧 Function `get_api_key`

```python
def get_api_key(config: dict[str, Any], provider: ProviderName) -> str
```

Return API key string for the provider (may be empty).

<details>
<summary>Code:</summary>

```python
def get_api_key(config: dict[str, Any], provider: ProviderName) -> str:
    key_name = str(_DEFAULTS[provider]["api_key_config"])
    return str(config.get(key_name, "")).strip()
```

</details>

## 🔧 Function `get_api_key_missing_message`

```python
def get_api_key_missing_message(provider: ProviderName) -> str
```

User-facing setup hint for a missing API key.

<details>
<summary>Code:</summary>

```python
def get_api_key_missing_message(provider: ProviderName) -> str:
    example = _DEFAULTS[provider]["example_key_file"]
    label = {
        "bothub": "BotHub",
        "bothub.ru": "BotHub.ru",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "gemini": "Gemini",
    }[provider]
    return (
        f"{label} API key is not configured.\n\n"
        f"Copy {example.replace('.txt', '.example.txt')} to {example} "
        "and add your access token (one line)."
    )
```

</details>

## 🔧 Function `get_chat_provider`

```python
def get_chat_provider(config: dict[str, Any]) -> ProviderName
```

Return the configured chat/vision provider (default bothub).

<details>
<summary>Code:</summary>

```python
def get_chat_provider(config: dict[str, Any]) -> ProviderName:
    ai_cfg = config.get("ai") or {}
    if not isinstance(ai_cfg, dict):
        return "bothub"
    return normalize_provider(str(ai_cfg.get("provider", "bothub")))
```

</details>

## 🔧 Function `get_connection_params_for_provider`

```python
def get_connection_params_for_provider(config: dict[str, Any], provider: ProviderName, *, for_speech: bool = False) -> tuple[str, str, str, str | None]
```

Return `(api_key, base_url, model, proxy_url)` for a provider.

<details>
<summary>Code:</summary>

```python
def get_connection_params_for_provider(
    config: dict[str, Any],
    provider: ProviderName,
    *,
    for_speech: bool = False,
) -> tuple[str, str, str, str | None]:
    settings = get_provider_settings(config, provider)
    api_key = get_api_key(config, provider)
    base_url = str(settings.get("base_url", "")).strip()
    if for_speech:
        model = str(settings.get("speech_model") or settings.get("model") or "").strip()
    else:
        model = str(settings.get("model") or "").strip()
    proxy_url = _resolve_config_proxy_url(config)
    return api_key, base_url, model, proxy_url
```

</details>

## 🔧 Function `get_max_image_side`

```python
def get_max_image_side(config: dict[str, Any], default: int = 1600) -> int
```

Return max image side from `ai`, then legacy `bothub`.

<details>
<summary>Code:</summary>

```python
def get_max_image_side(config: dict[str, Any], default: int = 1600) -> int:
    ai_cfg = config.get("ai") or {}
    if isinstance(ai_cfg, dict) and ai_cfg.get("max_image_side") is not None:
        try:
            return int(ai_cfg["max_image_side"])
        except (TypeError, ValueError):
            pass
    bothub_cfg = config.get("bothub") or {}
    if isinstance(bothub_cfg, dict) and bothub_cfg.get("max_image_side") is not None:
        try:
            return int(bothub_cfg["max_image_side"])
        except (TypeError, ValueError):
            pass
    return default
```

</details>

## 🔧 Function `get_provider_settings`

```python
def get_provider_settings(config: dict[str, Any], provider: ProviderName) -> dict[str, Any]
```

Return merged defaults + config section for a provider.

<details>
<summary>Code:</summary>

```python
def get_provider_settings(config: dict[str, Any], provider: ProviderName) -> dict[str, Any]:
    defaults = _DEFAULTS[provider]
    settings_key = str(defaults["settings_key"])
    section = config.get(settings_key) or {}
    if not isinstance(section, dict):
        section = {}
    merged = dict(defaults)
    merged.update(section)
    return merged
```

</details>

## 🔧 Function `get_speech_model_for_provider`

```python
def get_speech_model_for_provider(config: dict[str, Any], provider: ProviderName) -> str
```

Return speech model ID for the provider.

<details>
<summary>Code:</summary>

```python
def get_speech_model_for_provider(config: dict[str, Any], provider: ProviderName) -> str:
    settings = get_provider_settings(config, provider)
    return str(settings.get("speech_model") or settings.get("model") or "").strip()
```

</details>

## 🔧 Function `get_speech_provider`

```python
def get_speech_provider(config: dict[str, Any]) -> ProviderName
```

Return speech provider; empty `ai.speech_provider` means chat provider.

<details>
<summary>Code:</summary>

```python
def get_speech_provider(config: dict[str, Any]) -> ProviderName:
    ai_cfg = config.get("ai") or {}
    if not isinstance(ai_cfg, dict):
        return get_chat_provider(config)
    speech = str(ai_cfg.get("speech_provider", "")).strip()
    if not speech:
        return get_chat_provider(config)
    return normalize_provider(speech)
```

</details>

## 🔧 Function `is_bothub_router`

```python
def is_bothub_router(provider: ProviderName) -> bool
```

Return whether `provider` is a BotHub site router (`bothub` or `bothub.ru`).

<details>
<summary>Code:</summary>

```python
def is_bothub_router(provider: ProviderName) -> bool:
    return provider in BOTHUB_ROUTERS
```

</details>

## 🔧 Function `normalize_provider`

```python
def normalize_provider(value: str | None) -> ProviderName
```

Normalize a provider ID; unknown values fall back to bothub.

<details>
<summary>Code:</summary>

```python
def normalize_provider(value: str | None) -> ProviderName:
    name = (value or "bothub").strip().lower()
    alias = _PROVIDER_ALIASES.get(name)
    if alias is not None:
        return alias
    if name in PROVIDERS:
        return name  # type: ignore[return-value]
    return "bothub"
```

</details>

## 🔧 Function `other_bothub_router`

```python
def other_bothub_router(provider: ProviderName) -> ProviderName
```

Return the other BotHub site when `provider` is a BotHub router.

<details>
<summary>Code:</summary>

```python
def other_bothub_router(provider: ProviderName) -> ProviderName:
    if provider == "bothub":
        return "bothub.ru"
    return "bothub"
```

</details>

## 🔧 Function `provider_supports_speech`

```python
def provider_supports_speech(provider: ProviderName) -> bool
```

Return whether the provider can accept audio transcription requests.

<details>
<summary>Code:</summary>

```python
def provider_supports_speech(provider: ProviderName) -> bool:
    return provider != "anthropic"
```

</details>
