"""BotHub.chat / BotHub.ru failover: parallel API probes and API-error retry."""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
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
    get_provider_settings,
    get_speech_provider,
    is_bothub_router,
    normalize_provider,
    other_bothub_router,
)
from harrix_swiss_knife.integrations.http_transport import build_https_opener
from harrix_swiss_knife.paths import get_config_path

if TYPE_CHECKING:
    from collections.abc import Callable

TEMP_ACTIVE_PROVIDER_KEY = "ai_active_provider"
TEMP_ACTIVE_SPEECH_PROVIDER_KEY = "ai_active_speech_provider"
_ACTIVE_PROVIDER_KEY = "active_provider"
_ACTIVE_SPEECH_PROVIDER_KEY = "active_speech_provider"
_PROBE_TIMEOUT_SEC = 4.0
_NEGATIVE_CACHE_SEC = 60.0
_PROBE_UA = "Harrix-Swiss-Knife/1.0 (AI router probe)"
_HTTP_STATUS_RE = re.compile(r"HTTP\s+(\d{3})\b", re.IGNORECASE)
# Auth / rate-limit / gateway failures often work on the other BotHub site.
_FAILOVER_HTTP_STATUSES = frozenset({401, 403, 408, 425, 429, 500, 502, 503, 504})
# Monotonic deadline until which a router is treated as unreachable.
_router_down_until: dict[ProviderName, float] = {}


def bothub_probe_url(provider: ProviderName, config: dict[str, Any] | None = None) -> str:
    """Return the API probe URL for a BotHub router (`{base_url}/models`)."""
    settings = get_provider_settings(config or {}, provider)
    base_url = str(settings.get("base_url", "")).strip().rstrip("/")
    return f"{base_url}/models"


def clear_bothub_down_cache() -> None:
    """Clear the in-process negative cache of unreachable BotHub routers."""
    _router_down_until.clear()


def is_bothub_api_failover_error(message: str) -> bool:
    """Return whether an API error should be retried on the other BotHub site.

    Network/timeouts (no HTTP status) and selected HTTP statuses (5xx, 401/403,
    429, …) qualify. Client validation errors such as 400 do not.

    """
    match = _HTTP_STATUS_RE.search(message or "")
    if match is None:
        return True
    return int(match.group(1)) in _FAILOVER_HTTP_STATUSES


def mark_bothub_router_down(provider: ProviderName) -> None:
    """Remember that `provider` failed so the next request skips it for a minute."""
    if is_bothub_router(provider):
        _router_down_until[provider] = time.monotonic() + _NEGATIVE_CACHE_SEC


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

    """
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


def probe_bothub_site(url: str, proxy_url: str | None = None) -> bool:
    """Return whether `url` answers over HTTPS.

    Any HTTP response (including 4xx/5xx) counts as reachable. Timeouts,
    DNS failures, and connection errors count as unavailable.

    Args:

    - `url` (`str`): API probe URL (`{base_url}/models`).
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


def switch_bothub_router_after_api_failure(
    config: dict[str, Any],
    *,
    for_speech: bool = False,
    persist: Callable[[ProviderName, str | None], None] | None = None,
    config_path: Path | None = None,
) -> ProviderName | None:
    """Force-switch to the other BotHub router after a failed API call.

    Unlike `prepare_bothub_router`, this does not prefer the configured site when
    its homepage still answers — use it only after the live request failed.

    Args:

    - `config` (`dict[str, Any]`): In-memory config (mutated on switch).
    - `for_speech` (`bool`): Use the speech provider. Defaults to `False`.
    - `persist` (`Callable | None`): Override temp writer (tests).
    - `config_path` (`Path | None`): Main config file for temp write.

    Returns:

    - `ProviderName | None`: The new live router, or `None` when no switch.

    """
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


def _apply_router_in_memory(config: dict[str, Any], provider: ProviderName) -> None:
    ai = _ensure_ai_section(config)
    ai[_ACTIVE_PROVIDER_KEY] = provider
    speech = str(ai.get("speech_provider", "")).strip()
    if speech and is_bothub_router(normalize_provider(speech)):
        ai[_ACTIVE_SPEECH_PROVIDER_KEY] = provider


def _clear_router_down(provider: ProviderName) -> None:
    _router_down_until.pop(provider, None)


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


def _is_router_marked_down(provider: ProviderName) -> bool:
    until = _router_down_until.get(provider)
    if until is None:
        return False
    if time.monotonic() >= until:
        _router_down_until.pop(provider, None)
        return False
    return True


def _race_bothub_probes(
    preferred_url: str,
    alternate_url: str,
    proxy_url: str | None,
    probe: Callable[[str, str | None], bool],
) -> tuple[bool, bool]:
    """Probe both hosts in parallel; return as soon as the preferred site answers."""
    preferred_up = False
    alternate_up = False
    preferred_done = False
    alternate_done = False
    deadline = time.monotonic() + _PROBE_TIMEOUT_SEC + 0.5

    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_preferred = pool.submit(probe, preferred_url, proxy_url)
        fut_alternate = pool.submit(probe, alternate_url, proxy_url)
        pending = {fut_preferred, fut_alternate}
        while pending and time.monotonic() < deadline:
            done, pending = wait(
                pending,
                timeout=max(0.0, deadline - time.monotonic()),
                return_when=FIRST_COMPLETED,
            )
            if not done:
                break
            for fut in done:
                try:
                    result = bool(fut.result())
                except Exception:
                    result = False
                if fut is fut_preferred:
                    preferred_done = True
                    preferred_up = result
                    if preferred_up:
                        return True, alternate_up
                else:
                    alternate_done = True
                    alternate_up = result
            if preferred_done and not preferred_up and alternate_done:
                return False, alternate_up

        if not preferred_done:
            preferred_up = False
        if not alternate_done:
            try:
                alternate_up = bool(fut_alternate.result(timeout=0))
            except Exception:
                alternate_up = False
    return preferred_up, alternate_up


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


# Homepages kept for tests/docs that mention site hosts; probes use `bothub_probe_url`.
BOTHUB_PROBE_URLS: dict[ProviderName, str] = {
    "bothub": bothub_probe_url("bothub"),
    "bothub.ru": bothub_probe_url("bothub.ru"),
}
