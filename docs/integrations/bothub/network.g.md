---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `network.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `qnetwork_proxy_to_url`](#-function-qnetwork_proxy_to_url)
- [🔧 Function `resolve_bothub_proxy_url`](#-function-resolve_bothub_proxy_url)

</details>

## 🔧 Function `qnetwork_proxy_to_url`

```python
def qnetwork_proxy_to_url(proxy: QNetworkProxy | None = None) -> str | None
```

Resolve Qt proxy to HTTP proxy URL for urllib.

Priority:

- Explicit `proxy` if provided (used mostly for tests).
- System proxy configuration via `QNetworkProxyFactory.systemProxyForQuery` (PAC/WPAD).
- `QNetworkProxy.applicationProxy` fallback.

<details>
<summary>Code:</summary>

```python
def qnetwork_proxy_to_url(
    proxy: QNetworkProxy | None = None,
    *,
    system_proxies: Iterable[QNetworkProxy] | None = None,
) -> str | None:
    if proxy is not None:
        return _proxy_to_url(proxy)

    if system_proxies is None:
        query = QNetworkProxyQuery(QUrl("https://bothub.chat/"))
        system_proxies = QNetworkProxyFactory.systemProxyForQuery(query)

    for p in system_proxies:
        url = _proxy_to_url(p)
        if url:
            return url

    return _proxy_to_url(QNetworkProxy.applicationProxy())
```

</details>

## 🔧 Function `resolve_bothub_proxy_url`

```python
def resolve_bothub_proxy_url(app_config: dict[str, Any]) -> str | None
```

Resolve BotHub HTTP proxy from config, Qt, environment, and system settings.

<details>
<summary>Code:</summary>

```python
def resolve_bothub_proxy_url(app_config: dict[str, Any]) -> str | None:
    bothub_cfg = app_config.get("bothub") or {}
    config_proxy = str(bothub_cfg.get("proxy", "")).strip() or None
    qt_proxy_url = qnetwork_proxy_to_url()
    return resolve_proxy_url(config_proxy=config_proxy, qt_proxy_url=qt_proxy_url)
```

</details>
