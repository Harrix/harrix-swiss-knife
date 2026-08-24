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

Write `ai.provider` (and optional speech provider) into `config.json`.

The file is loaded as raw JSON so `snippet:` values stay unexpanded.

Args:

- `provider` (`ProviderName`): New chat router ID.
- `speech_provider` (`str | None`): New speech router, or `None` to leave it.
- `config_path` (`Path | None`): Config file. Defaults to the project config.

<details>
<summary>Code:</summary>

```python
def persist_ai_provider(
    provider: ProviderName,
    *,
    speech_provider: str | None = None,
    config_path: Path | None = None,
) -> None:
    path = config_path or get_config_path()
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    ai = raw.get("ai")
    if not isinstance(ai, dict):
        ai = {}
        raw["ai"] = ai
    ai["provider"] = provider
    if speech_provider is not None:
        ai["speech_provider"] = speech_provider
    path.write_text(h.dev.dumps_pretty_json(raw), encoding="utf-8")
```

</details>

## 🔧 Function `prepare_bothub_router`

```python
def prepare_bothub_router(config: dict[str, Any], *, for_speech: bool = False, proxy_url: str | None = None, probe: Callable[[str, str | None], bool] | None = None, persist: Callable[[ProviderName, str | None], None] | None = None) -> ProviderName | None
```

If the active BotHub site is down, switch once to the other when it is up.

Persists the new router only after the other site answers. If both sites
are down, `config.json` stays on the previous provider. The next
independent AI request can try failover again.

Args:

- [`config`](../../actions/common/base.g.md#%EF%B8%8F-method-config-property) (`dict[str, Any]`): In-memory application config (mutated on switch).
- `for_speech` (`bool`): Use the speech provider. Defaults to `False`.
- `proxy_url` (`str | None`): Optional HTTPS proxy for the probe.
- `probe` (`Callable | None`): Override reachability check (tests).
- `persist` (`Callable | None`): Override config writer (tests).

Returns:

- `ProviderName | None`: The router written to config, or `None` if unchanged.

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
) -> ProviderName | None:
    current = get_speech_provider(config) if for_speech else get_chat_provider(config)
    if not is_bothub_router(current):
        return None

    alternate = other_bothub_router(current)
    if not _has_usable_key(config, alternate):
        return None

    check = probe or probe_bothub_site
    if check(BOTHUB_PROBE_URLS[current], proxy_url):
        return None
    if not check(BOTHUB_PROBE_URLS[alternate], proxy_url):
        return None

    _apply_router_in_memory(config, alternate)
    writer = persist or (lambda provider, speech: persist_ai_provider(provider, speech_provider=speech))
    speech_to_write = _speech_provider_after_switch(config, alternate)
    with suppress(OSError, TypeError, ValueError, json.JSONDecodeError):
        writer(alternate, speech_to_write)
    return alternate
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
