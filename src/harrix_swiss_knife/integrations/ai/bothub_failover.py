"""One-shot BotHub site failover when bothub.chat or bothub.ru is unreachable."""

from __future__ import annotations

import json
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request

import harrix_pylib as h

from harrix_swiss_knife.integrations.ai.config import (
    ProviderName,
    get_api_key,
    get_chat_provider,
    get_preferred_chat_provider,
    get_preferred_speech_provider,
    get_speech_provider,
    is_bothub_router,
    normalize_provider,
    other_bothub_router,
)
from harrix_swiss_knife.integrations.http_transport import build_https_opener
from harrix_swiss_knife.paths import get_config_path

if TYPE_CHECKING:
    from collections.abc import Callable

BOTHUB_PROBE_URLS: dict[ProviderName, str] = {
    "bothub": "https://bothub.chat/",
    "bothub.ru": "https://bothub.ru/",
}
TEMP_ACTIVE_PROVIDER_KEY = "ai_active_provider"
TEMP_ACTIVE_SPEECH_PROVIDER_KEY = "ai_active_speech_provider"
_ACTIVE_PROVIDER_KEY = "active_provider"
_ACTIVE_SPEECH_PROVIDER_KEY = "active_speech_provider"
_PROBE_TIMEOUT_SEC = 5
_PROBE_UA = "Harrix-Swiss-Knife/1.0 (AI router probe)"


def persist_ai_provider(
    provider: ProviderName,
    *,
    speech_provider: str | None = None,
    config_path: Path | None = None,
) -> None:
    """Write the live BotHub router into `config-temp.json`.

    `ai.provider` in `config.json` stays the preferred site.

    Args:

    - `provider` (`ProviderName`): Live chat router ID.
    - `speech_provider` (`str | None`): Live speech router, or `None` to leave it.
    - `config_path` (`Path | None`): Main config file. Defaults to the project config.

    """
    path_str = str(config_path or get_config_path())
    _ensure_temp_config_file(path_str)
    h.dev.config_update_value(TEMP_ACTIVE_PROVIDER_KEY, provider, path_str, is_temp=True)
    if speech_provider is not None:
        h.dev.config_update_value(TEMP_ACTIVE_SPEECH_PROVIDER_KEY, speech_provider, path_str, is_temp=True)


def prepare_bothub_router(
    config: dict[str, Any],
    *,
    for_speech: bool = False,
    proxy_url: str | None = None,
    probe: Callable[[str, str | None], bool] | None = None,
    persist: Callable[[ProviderName, str | None], None] | None = None,
    config_path: Path | None = None,
) -> ProviderName | None:
    """Use the preferred BotHub site when it is up; otherwise the other site.

    Preferred `ai.provider` / `ai.speech_provider` stay in `config.json`. The
    live router is stored in `config-temp.json` and on `ai.active_provider`.
    When the preferred site comes back, the next request fails back to it.

    Args:

    - `config` (`dict[str, Any]`): In-memory application config (mutated on switch).
    - `for_speech` (`bool`): Use the speech provider. Defaults to `False`.
    - `proxy_url` (`str | None`): Optional HTTPS proxy for the probe.
    - `probe` (`Callable | None`): Override reachability check (tests).
    - `persist` (`Callable | None`): Override temp writer (tests).
    - `config_path` (`Path | None`): Main config file for temp read/write.

    Returns:

    - `ProviderName | None`: The router written to temp, or `None` if unchanged.

    """
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
    ai = _ensure_ai_section(config)
    ai[_ACTIVE_PROVIDER_KEY] = provider
    speech = str(ai.get("speech_provider", "")).strip()
    if speech and is_bothub_router(normalize_provider(speech)):
        ai[_ACTIVE_SPEECH_PROVIDER_KEY] = provider


def _commit_router_if_changed(
    config: dict[str, Any],
    provider: ProviderName,
    *,
    for_speech: bool,
    persist: Callable[[ProviderName, str | None], None] | None,
    config_path: Path,
) -> ProviderName | None:
    current = get_speech_provider(config) if for_speech else get_chat_provider(config)
    if current == provider:
        return None
    _apply_router_in_memory(config, provider)
    writer = persist or (
        lambda next_provider, speech: persist_ai_provider(
            next_provider,
            speech_provider=speech,
            config_path=config_path,
        )
    )
    speech_to_write = _speech_provider_after_switch(config, provider)
    with suppress(OSError, TypeError, ValueError, json.JSONDecodeError):
        writer(provider, speech_to_write)
    return provider


def _ensure_ai_section(config: dict[str, Any]) -> dict[str, Any]:
    ai = config.get("ai")
    if not isinstance(ai, dict):
        ai = {}
        config["ai"] = ai
    return ai


def _ensure_temp_config_file(config_path: str) -> None:
    temp_path = _sibling_temp_config_path(config_path)
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_path.exists() or temp_path.stat().st_size == 0:
        temp_path.write_text("{}", encoding="utf-8")


def _has_usable_key(config: dict[str, Any], provider: ProviderName) -> bool:
    key = get_api_key(config, provider)
    return bool(key) and not key.startswith("paste-your-")


def _hydrate_active_from_temp(config: dict[str, Any], config_path: str) -> None:
    ai = _ensure_ai_section(config)
    if not str(ai.get(_ACTIVE_PROVIDER_KEY) or "").strip():
        stored = _read_temp_key(config_path, TEMP_ACTIVE_PROVIDER_KEY)
        if stored and is_bothub_router(normalize_provider(stored)):
            ai[_ACTIVE_PROVIDER_KEY] = normalize_provider(stored)
    if not str(ai.get(_ACTIVE_SPEECH_PROVIDER_KEY) or "").strip():
        stored = _read_temp_key(config_path, TEMP_ACTIVE_SPEECH_PROVIDER_KEY)
        if stored and is_bothub_router(normalize_provider(stored)):
            ai[_ACTIVE_SPEECH_PROVIDER_KEY] = normalize_provider(stored)


def _read_temp_key(config_path: str, key: str) -> str:
    try:
        data = h.dev.config_load(config_path, is_temp=True, resolve_snippets=False)
    except (FileNotFoundError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return ""
    if not isinstance(data, dict):
        return ""
    return str(data.get(key) or "").strip()


def _resolve_config_file(config_path: str) -> Path:
    path = Path(config_path)
    if path.is_absolute():
        return path
    return Path(h.dev.get_project_root()) / path


def _sibling_temp_config_path(config_path: str) -> Path:
    path = _resolve_config_file(config_path)
    return path.with_name(f"{path.stem}-temp{path.suffix}")


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
