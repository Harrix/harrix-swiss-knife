---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `bothub_failover.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `persist_ai_provider`](#-function-persist_ai_provider)
- [🔧 Function `prepare_bothub_router`](#-function-prepare_bothub_router)
- [🔧 Function `probe_bothub_site`](#-function-probe_bothub_site)

</details>

## 🔧 Function `persist_ai_provider`

```python
def persist_ai_provider(provider: ProviderName, *, speech_provider: str | None = None, config_path: Path | None = None) -> None
```

Write the live BotHub router into `config-temp.json`.

`ai.provider` in `config.json` stays the preferred site.

Args:

- `provider` (`ProviderName`): Live chat router ID.
- `speech_provider` (`str | None`): Live speech router, or `None` to leave it.
- `config_path` (`Path | None`): Main config file. Defaults to the project config.

<details>
<summary>Code:</summary>

```python
def persist_ai_provider(
    provider: ProviderName,
    *,
    speech_provider: str | None = None,
    config_path: Path | None = None,
) -> None:
    path_str = str(config_path or get_config_path())
    _ensure_temp_config_file(path_str)
    h.dev.config_update_value(TEMP_ACTIVE_PROVIDER_KEY, provider, path_str, is_temp=True)
    if speech_provider is not None:
        h.dev.config_update_value(TEMP_ACTIVE_SPEECH_PROVIDER_KEY, speech_provider, path_str, is_temp=True)
```

</details>

## 🔧 Function `prepare_bothub_router`

```python
def prepare_bothub_router(config: dict[str, Any], *, for_speech: bool = False, proxy_url: str | None = None, probe: Callable[[str, str | None], bool] | None = None, persist: Callable[[ProviderName, str | None], None] | None = None, config_path: Path | None = None) -> ProviderName | None
```

Use the preferred BotHub site when it is up; otherwise the other site.

Preferred `ai.provider` / `ai.speech_provider` stay in `config.json`. The
live router is stored in `config-temp.json` and on `ai.active_provider`.
When the preferred site comes back, the next request fails back to it.

Args:

- [`config`](../../actions/common/base.g.md#%EF%B8%8F-method-config-property) (`dict[str, Any]`): In-memory application config (mutated on switch).
- `for_speech` (`bool`): Use the speech provider. Defaults to `False`.
- `proxy_url` (`str | None`): Optional HTTPS proxy for the probe.
- `probe` (`Callable | None`): Override reachability check (tests).
- `persist` (`Callable | None`): Override temp writer (tests).
- `config_path` (`Path | None`): Main config file for temp read/write.

Returns:

- `ProviderName | None`: The router written to temp, or `None` if unchanged.

<details>
<summary>Code:</summary>

```python
def prepare_bothub_router(
    config: dict[str, Any],
    *,
    for_speech: bool = False,
    proxy_url: str | None = None,
    probe: Callable[[str, str | None], bool] | None = None,
    persist: Callable[[ProviderName, str | None], None] | None = None,
    config_path: Path | None = None,
) -> ProviderName | None:
    preferred = get_preferred_speech_provider(config) if for_speech else get_preferred_chat_provider(config)
    if not is_bothub_router(preferred):
        return None

    path = config_path or get_config_path()
    path_str = str(path)
    _hydrate_active_from_temp(config, path_str)

    check = probe or probe_bothub_site
    if check(BOTHUB_PROBE_URLS[preferred], proxy_url):
        return _commit_router_if_changed(
            config,
            preferred,
            for_speech=for_speech,
            persist=persist,
            config_path=path,
        )

    alternate = other_bothub_router(preferred)
    if not _has_usable_key(config, alternate):
        return None
    if not check(BOTHUB_PROBE_URLS[alternate], proxy_url):
        return None
    return _commit_router_if_changed(
        config,
        alternate,
        for_speech=for_speech,
        persist=persist,
        config_path=path,
    )
```

</details>

## 🔧 Function `probe_bothub_site`

```python
def probe_bothub_site(url: str, proxy_url: str | None = None) -> bool
```

Return whether `url` answers over HTTPS.

Any HTTP response (including 4xx/5xx) counts as reachable. Timeouts,
DNS failures, and connection errors count as unavailable.

Args:

- `url` (`str`): Site to probe (`https://bothub.chat/` or `https://bothub.ru/`).
- `proxy_url` (`str | None`): Optional HTTPS proxy.

Returns:

- `bool`: `True` when the host responded.

<details>
<summary>Code:</summary>

```python
def probe_bothub_site(url: str, proxy_url: str | None = None) -> bool:
    if urlsplit(url).scheme != "https":
        return False
    opener = build_https_opener(proxy_url)
    request = Request(url, method="GET", headers={"User-Agent": _PROBE_UA})  # noqa: S310
    try:
        with opener.open(request, timeout=_PROBE_TIMEOUT_SEC) as response:
            response.read(64)
    except HTTPError:
        return True
    except (OSError, URLError, TimeoutError, ValueError):
        return False
    return True
```

</details>
