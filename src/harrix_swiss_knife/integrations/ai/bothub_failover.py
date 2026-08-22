"""One-shot BotHub site failover when bothub.chat or bothub.ru is unreachable."""

from __future__ import annotations

import json
from contextlib import suppress
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request

import harrix_pylib as h

from harrix_swiss_knife.integrations.ai.config import (
    ProviderName,
    get_api_key,
    get_chat_provider,
    get_speech_provider,
    is_bothub_router,
    normalize_provider,
    other_bothub_router,
)
from harrix_swiss_knife.integrations.http_transport import build_https_opener
from harrix_swiss_knife.paths import get_config_path

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

BOTHUB_PROBE_URLS: dict[ProviderName, str] = {
    "bothub": "https://bothub.chat/",
    "bothub.ru": "https://bothub.ru/",
}
_PROBE_TIMEOUT_SEC = 5
_PROBE_UA = "Harrix-Swiss-Knife/1.0 (AI router probe)"


def persist_ai_provider(
    provider: ProviderName,
    *,
    speech_provider: str | None = None,
    config_path: Path | None = None,
) -> None:
    """Write `ai.provider` (and optional speech provider) into `config.json`.

    The file is loaded as raw JSON so `snippet:` values stay unexpanded.

    Args:

    - `provider` (`ProviderName`): New chat router ID.
    - `speech_provider` (`str | None`): New speech router, or `None` to leave it.
    - `config_path` (`Path | None`): Config file. Defaults to the project config.

    """
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


def prepare_bothub_router(
    config: dict[str, Any],
    *,
    for_speech: bool = False,
    proxy_url: str | None = None,
    probe: Callable[[str, str | None], bool] | None = None,
    persist: Callable[[ProviderName, str | None], None] | None = None,
) -> ProviderName | None:
    """If the active BotHub site is down, switch once to the other and persist it.

    Does not switch back when the other site is also down. The next independent
    AI request can failover again.

    Args:

    - `config` (`dict[str, Any]`): In-memory application config (mutated on switch).
    - `for_speech` (`bool`): Use the speech provider. Defaults to `False`.
    - `proxy_url` (`str | None`): Optional HTTPS proxy for the probe.
    - `probe` (`Callable | None`): Override reachability check (tests).
    - `persist` (`Callable | None`): Override config writer (tests).

    Returns:

    - `ProviderName | None`: The router written to config, or `None` if unchanged.

    """
    current = get_speech_provider(config) if for_speech else get_chat_provider(config)
    if not is_bothub_router(current):
        return None

    alternate = other_bothub_router(current)
    if not _has_usable_key(config, alternate):
        return None

    check = probe or probe_bothub_site
    if check(BOTHUB_PROBE_URLS[current], proxy_url):
        return None

    _apply_router_in_memory(config, alternate)
    writer = persist or (lambda provider, speech: persist_ai_provider(provider, speech_provider=speech))
    speech_to_write = _speech_provider_after_switch(config, alternate)
    with suppress(OSError, TypeError, ValueError, json.JSONDecodeError):
        writer(alternate, speech_to_write)
    return alternate


def probe_bothub_site(url: str, proxy_url: str | None = None) -> bool:
    """Return whether `url` answers over HTTPS.

    Any HTTP response (including 4xx/5xx) counts as reachable. Timeouts,
    DNS failures, and connection errors count as unavailable.

    Args:

    - `url` (`str`): Site to probe (`https://bothub.chat/` or `https://bothub.ru/`).
    - `proxy_url` (`str | None`): Optional HTTPS proxy.

    Returns:

    - `bool`: `True` when the host responded.

    """
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


def _apply_router_in_memory(config: dict[str, Any], provider: ProviderName) -> None:
    ai = config.get("ai")
    if not isinstance(ai, dict):
        ai = {}
        config["ai"] = ai
    ai["provider"] = provider
    speech = str(ai.get("speech_provider", "")).strip()
    if speech and is_bothub_router(normalize_provider(speech)):
        ai["speech_provider"] = provider


def _has_usable_key(config: dict[str, Any], provider: ProviderName) -> bool:
    key = get_api_key(config, provider)
    return bool(key) and not key.startswith("paste-your-")


def _speech_provider_after_switch(config: dict[str, Any], new_provider: ProviderName) -> str | None:
    ai = config.get("ai")
    if not isinstance(ai, dict):
        return None
    speech = str(ai.get("speech_provider", "")).strip()
    if not speech:
        return None
    if is_bothub_router(normalize_provider(speech)):
        return new_provider
    return None
