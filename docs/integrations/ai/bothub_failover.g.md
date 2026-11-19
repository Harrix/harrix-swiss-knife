---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `bothub_failover.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `bothub_probe_url`](#-function-bothub_probe_url)
- [🔧 Function `clear_bothub_down_cache`](#-function-clear_bothub_down_cache)
- [🔧 Function `is_bothub_api_failover_error`](#-function-is_bothub_api_failover_error)
- [🔧 Function `mark_bothub_router_down`](#-function-mark_bothub_router_down)
- [🔧 Function `persist_ai_provider`](#-function-persist_ai_provider)
- [🔧 Function `prepare_bothub_router`](#-function-prepare_bothub_router)
- [🔧 Function `probe_bothub_site`](#-function-probe_bothub_site)
- [🔧 Function `switch_bothub_router_after_api_failure`](#-function-switch_bothub_router_after_api_failure)

</details>

## 🔧 Function `bothub_probe_url`

```python
def bothub_probe_url(provider: ProviderName, config: dict[str, Any] | None = None) -> str
```

Return the API probe URL for a BotHub router (`{base_url}/models`).

<details>
<summary>Code:</summary>

```python
def bothub_probe_url(provider: ProviderName, config: dict[str, Any] | None = None) -> str:
    settings = get_provider_settings(config or {}, provider)
    base_url = str(settings.get("base_url", "")).strip().rstrip("/")
    return f"{base_url}/models"
```

</details>

## 🔧 Function `clear_bothub_down_cache`

```python
def clear_bothub_down_cache() -> None
```

Clear the in-process negative cache of unreachable BotHub routers.

<details>
<summary>Code:</summary>

```python
def clear_bothub_down_cache() -> None:
    _router_down_until.clear()
```

</details>

## 🔧 Function `is_bothub_api_failover_error`

```python
def is_bothub_api_failover_error(message: str) -> bool
```

Return whether an API error should be retried on the other BotHub site.

Network/timeouts (no HTTP status) and selected HTTP statuses (5xx, 401/403,
429, …) qualify. Client validation errors such as 400 do not.

<details>
<summary>Code:</summary>

```python
def is_bothub_api_failover_error(message: str) -> bool:
    match = _HTTP_STATUS_RE.search(message or "")
    if match is None:
        return True
    return int(match.group(1)) in _FAILOVER_HTTP_STATUSES
```

</details>

## 🔧 Function `mark_bothub_router_down`

```python
def mark_bothub_router_down(provider: ProviderName) -> None
```

Remember that `provider` failed so the next request skips it for a minute.

<details>
<summary>Code:</summary>

```python
def mark_bothub_router_down(provider: ProviderName) -> None:
    if is_bothub_router(provider):
        _router_down_until[provider] = time.monotonic() + _NEGATIVE_CACHE_SEC
```

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
API hosts are probed in parallel (`{base_url}/models`). When the preferred
site is recently down, the alternate is used without waiting for another
preferred probe.

Args:

- `config` (`dict[str, Any]`): In-memory application config (mutated on switch).
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
    alternate = other_bothub_router(preferred)
    has_alternate = _has_usable_key(config, alternate)

    if _is_router_marked_down(preferred) and has_alternate:
        return _commit_router_if_changed(
            config,
            alternate,
            for_speech=for_speech,
            persist=persist,
            config_path=path,
        )

    preferred_url = bothub_probe_url(preferred, config)
    if not has_alternate:
        if check(preferred_url, proxy_url):
            _clear_router_down(preferred)
            return _commit_router_if_changed(
                config,
                preferred,
                for_speech=for_speech,
                persist=persist,
                config_path=path,
            )
        mark_bothub_router_down(preferred)
        return None

    preferred_up, alternate_up = _race_bothub_probes(
        preferred_url,
        bothub_probe_url(alternate, config),
        proxy_url,
        check,
    )
    if preferred_up:
        _clear_router_down(preferred)
        return _commit_router_if_changed(
            config,
            preferred,
            for_speech=for_speech,
            persist=persist,
            config_path=path,
        )

    mark_bothub_router_down(preferred)
    if alternate_up:
        return _commit_router_if_changed(
            config,
            alternate,
            for_speech=for_speech,
            persist=persist,
            config_path=path,
        )
    return None
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

- `url` (`str`): API probe URL (`{base_url}/models`).
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

## 🔧 Function `switch_bothub_router_after_api_failure`

```python
def switch_bothub_router_after_api_failure(config: dict[str, Any], *, for_speech: bool = False, persist: Callable[[ProviderName, str | None], None] | None = None, config_path: Path | None = None) -> ProviderName | None
```

Force-switch to the other BotHub router after a failed API call.

Unlike [`prepare_bothub_router`](#-function-prepare_bothub_router), this does not prefer the configured site when
its homepage still answers — use it only after the live request failed.

Args:

- `config` (`dict[str, Any]`): In-memory config (mutated on switch).
- `for_speech` (`bool`): Use the speech provider. Defaults to `False`.
- `persist` (`Callable | None`): Override temp writer (tests).
- `config_path` (`Path | None`): Main config file for temp write.

Returns:

- `ProviderName | None`: The new live router, or `None` when no switch.

<details>
<summary>Code:</summary>

```python
def switch_bothub_router_after_api_failure(
    config: dict[str, Any],
    *,
    for_speech: bool = False,
    persist: Callable[[ProviderName, str | None], None] | None = None,
    config_path: Path | None = None,
) -> ProviderName | None:
    current = get_speech_provider(config) if for_speech else get_chat_provider(config)
    if not is_bothub_router(current):
        return None
    alternate = other_bothub_router(current)
    if not _has_usable_key(config, alternate):
        return None
    mark_bothub_router_down(current)
    path = config_path or get_config_path()
    return _commit_router_if_changed(
        config,
        alternate,
        for_speech=for_speech,
        persist=persist,
        config_path=path,
    )
```

</details>
