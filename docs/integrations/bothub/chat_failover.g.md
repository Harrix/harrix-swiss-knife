---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chat_failover.py`

## 🔧 Function `chat_completion_with_bothub_failover`

```python
def chat_completion_with_bothub_failover(config: dict[str, Any], prompt_text: str, *, for_speech: bool = False, images: Sequence[tuple[bytes, str]] | None = None, audio: tuple[bytes, str] | None = None) -> str
```

Prepare the BotHub router, call chat, and retry once on the other site if needed.

Raises:

- [`BotHubApiError`](../bothub_client.g.md#-constant-bothubapierror): When both attempts fail (or failover does not apply).

<details>
<summary>Code:</summary>

```python
def chat_completion_with_bothub_failover(
    config: dict[str, Any],
    prompt_text: str,
    *,
    for_speech: bool = False,
    images: Sequence[tuple[bytes, str]] | None = None,
    audio: tuple[bytes, str] | None = None,
) -> str:
    prepare_bothub_router(config, for_speech=for_speech, proxy_url=get_proxy_url(config))
    provider = get_active_provider(config, for_speech=for_speech)
    api_key, base_url, model, proxy_url = get_connection_params(config, for_speech=for_speech)
    try:
        return chat_completion(
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=prompt_text,
            images=images,
            audio=audio,
            proxy_url=proxy_url,
            provider=provider,
        )
    except BotHubApiError as exc:
        if not is_bothub_router(provider) or not is_bothub_api_failover_error(str(exc)):
            raise
        if switch_bothub_router_after_api_failure(config, for_speech=for_speech) is None:
            raise
        provider = get_active_provider(config, for_speech=for_speech)
        api_key, base_url, model, proxy_url = get_connection_params(config, for_speech=for_speech)
        return chat_completion(
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=prompt_text,
            images=images,
            audio=audio,
            proxy_url=proxy_url,
            provider=provider,
        )
```

</details>
