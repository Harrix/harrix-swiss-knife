"""Tests for BotHub.chat / BotHub.ru one-shot router failover."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from harrix_swiss_knife.integrations.ai.bothub_failover import (
    TEMP_ACTIVE_PROVIDER_KEY,
    TEMP_ACTIVE_SPEECH_PROVIDER_KEY,
    bothub_probe_url,
    clear_bothub_down_cache,
    is_bothub_api_failover_error,
    mark_bothub_router_down,
    persist_ai_provider,
    prepare_bothub_router,
    switch_bothub_router_after_api_failure,
)
from harrix_swiss_knife.integrations.ai.config import get_chat_provider, get_preferred_chat_provider


def test_bothub_probe_url_uses_models_endpoint() -> None:
    assert bothub_probe_url("bothub").endswith("/models")
    assert "bothub.chat" in bothub_probe_url("bothub")
    assert bothub_probe_url("bothub.ru").endswith("/models")
    assert "openai.bothub.ru" in bothub_probe_url("bothub.ru")


def test_is_bothub_api_failover_error_for_gateway_and_network() -> None:
    assert is_bothub_api_failover_error("HTTP 502: <html>Bad Gateway</html>")
    assert is_bothub_api_failover_error("HTTP 503: unavailable")
    assert is_bothub_api_failover_error("HTTP 401: UNAUTHORIZED")
    assert is_bothub_api_failover_error("Network error: timed out")
    assert not is_bothub_api_failover_error("HTTP 400: bad request")
    assert not is_bothub_api_failover_error("HTTP 404: missing")


def test_persist_ai_provider_keeps_main_config_formatting(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    text = (
        '{\n  "block_drives": ["E", "F"],\n  "npm_packages": ["npm-check-updates", "prettier"],\n'
        '  "ai": {"provider": "bothub"}\n}\n'
    )
    path.write_text(text, encoding="utf-8")
    persist_ai_provider("bothub.ru", speech_provider="bothub.ru", config_path=path)
    assert path.read_text(encoding="utf-8") == text
    temp = json.loads((tmp_path / "config-temp.json").read_text(encoding="utf-8"))
    assert temp[TEMP_ACTIVE_PROVIDER_KEY] == "bothub.ru"
    assert temp[TEMP_ACTIVE_SPEECH_PROVIDER_KEY] == "bothub.ru"


def test_persist_ai_provider_writes_temp_not_main_config(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    original = {
        "editor": "cursor",
        "bothub_api_key": "snippet:api-keys/bothub-api-key.txt",
        "ai": {"provider": "bothub", "speech_provider": "", "proxy": ""},
    }
    path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
    persist_ai_provider("bothub.ru", config_path=path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["ai"]["provider"] == "bothub"
    assert data["ai"]["speech_provider"] == ""
    assert data["bothub_api_key"] == "snippet:api-keys/bothub-api-key.txt"
    assert data["editor"] == "cursor"
    temp = json.loads((tmp_path / "config-temp.json").read_text(encoding="utf-8"))
    assert temp[TEMP_ACTIVE_PROVIDER_KEY] == "bothub.ru"
    assert TEMP_ACTIVE_SPEECH_PROVIDER_KEY not in temp


def test_prepare_does_not_switch_openai() -> None:
    config = {"ai": {"provider": "openai"}, "openai_api_key": "sk", "bothub_ru_api_key": "ru-key"}
    switched = prepare_bothub_router(config, probe=lambda _url, _proxy: False)
    assert switched is None
    assert get_chat_provider(config) == "openai"


def test_prepare_does_not_switch_when_preferred_site_is_up(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    persisted: list[str] = []
    switched = prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: True,
        persist=lambda provider, _speech: persisted.append(provider),
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched is None
    assert get_preferred_chat_provider(config) == "bothub"
    assert get_chat_provider(config) == "bothub"
    assert persisted == []


def test_prepare_does_not_switch_without_alternate_key(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    config["bothub_ru_api_key"] = ""
    switched = prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: False,
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched is None
    assert get_chat_provider(config) == "bothub"


def test_prepare_fails_back_to_preferred_when_it_is_up_again(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    config["ai"]["active_provider"] = "bothub.ru"
    persisted: list[str] = []
    switched = prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: True,
        persist=lambda provider, _speech: persisted.append(provider),
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched == "bothub"
    assert config["ai"]["provider"] == "bothub"
    assert get_chat_provider(config) == "bothub"
    assert persisted == ["bothub"]


def test_prepare_from_bothub_ru_switches_to_bothub(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    config["ai"]["provider"] = "bothub.ru"
    config_path = _isolated_config_path(tmp_path)
    switched = prepare_bothub_router(
        config,
        probe=_probe_hosts("bothub.chat"),
        persist=lambda _provider, _speech: None,
        config_path=config_path,
    )
    assert switched == "bothub"
    assert config["ai"]["provider"] == "bothub.ru"
    assert get_chat_provider(config) == "bothub"


def test_prepare_hydrates_active_router_from_temp(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    (tmp_path / "config-temp.json").write_text(
        json.dumps({TEMP_ACTIVE_PROVIDER_KEY: "bothub.ru"}),
        encoding="utf-8",
    )
    config = _bothub_pair_config()
    switched = prepare_bothub_router(
        config,
        probe=_probe_hosts("bothub.ru"),
        persist=lambda _provider, _speech: None,
        config_path=path,
    )
    assert switched is None
    assert config["ai"]["provider"] == "bothub"
    assert get_chat_provider(config) == "bothub.ru"


def test_prepare_keeps_old_provider_when_both_sites_are_down(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    persisted: list[str] = []
    switched = prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: False,
        persist=lambda provider, _speech: persisted.append(provider),
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched is None
    assert get_chat_provider(config) == "bothub"
    assert persisted == []


def test_prepare_reprobes_preferred_after_negative_cache_cleared(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    config["ai"]["active_provider"] = "bothub.ru"
    mark_bothub_router_down("bothub")
    clear_bothub_down_cache()
    switched = prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: True,
        persist=lambda _provider, _speech: None,
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched == "bothub"
    assert get_chat_provider(config) == "bothub"


def test_prepare_switches_once_when_preferred_site_is_down(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    persisted: list[tuple[str, str | None]] = []
    switched = prepare_bothub_router(
        config,
        probe=_probe_hosts("bothub.ru"),
        persist=lambda provider, speech: persisted.append((provider, speech)),
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched == "bothub.ru"
    assert get_preferred_chat_provider(config) == "bothub"
    assert config["ai"]["provider"] == "bothub"
    assert get_chat_provider(config) == "bothub.ru"
    assert persisted == [("bothub.ru", None)]


def test_prepare_updates_speech_active_when_it_is_a_bothub_router(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    config["ai"]["speech_provider"] = "bothub"
    persisted: list[tuple[str, str | None]] = []
    prepare_bothub_router(
        config,
        probe=_probe_hosts("bothub.ru"),
        persist=lambda provider, speech: persisted.append((provider, speech)),
        config_path=_isolated_config_path(tmp_path),
    )
    assert config["ai"]["speech_provider"] == "bothub"
    assert config["ai"]["active_speech_provider"] == "bothub.ru"
    assert persisted == [("bothub.ru", "bothub.ru")]


def test_prepare_uses_negative_cache_without_probing_preferred(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    probed: list[str] = []

    def probe(url: str, _proxy: str | None) -> bool:
        probed.append(url)
        return "openai.bothub.ru" in url

    mark_bothub_router_down("bothub")
    switched = prepare_bothub_router(
        config,
        probe=probe,
        persist=lambda _provider, _speech: None,
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched == "bothub.ru"
    assert probed == []
    assert get_chat_provider(config) == "bothub.ru"


def test_switch_bothub_router_after_api_failure_from_ru_to_chat(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    config["ai"]["provider"] = "bothub.ru"
    config["ai"]["active_provider"] = "bothub.ru"
    persisted: list[str] = []
    switched = switch_bothub_router_after_api_failure(
        config,
        persist=lambda provider, _speech: persisted.append(provider),
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched == "bothub"
    assert get_preferred_chat_provider(config) == "bothub.ru"
    assert get_chat_provider(config) == "bothub"
    assert persisted == ["bothub"]


def test_switch_bothub_router_after_api_failure_without_alternate_key(tmp_path: Path) -> None:
    config = _bothub_pair_config()
    config["ai"]["provider"] = "bothub.ru"
    config["ai"]["active_provider"] = "bothub.ru"
    config["bothub_api_key"] = ""
    switched = switch_bothub_router_after_api_failure(
        config,
        config_path=_isolated_config_path(tmp_path),
    )
    assert switched is None
    assert get_chat_provider(config) == "bothub.ru"


def _bothub_pair_config() -> dict[str, Any]:
    return {
        "ai": {"provider": "bothub", "speech_provider": ""},
        "bothub_api_key": "chat-key",
        "bothub_ru_api_key": "ru-key",
        "bothub": {"base_url": "https://bothub.chat/api/v2/openai/v1", "model": "gpt-5.5"},
        "bothub_ru": {"base_url": "https://openai.bothub.ru/v1", "model": "gpt-5.5"},
    }


@pytest.fixture(autouse=True)
def _clear_bothub_down_cache() -> None:
    clear_bothub_down_cache()


def _isolated_config_path(tmp_path: Path) -> Path:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    (tmp_path / "config-temp.json").write_text("{}", encoding="utf-8")
    return config_path


def _probe_hosts(*up_hosts: str) -> Callable[[str, str | None], bool]:
    def probe(url: str, _proxy: str | None) -> bool:
        return any(host in url for host in up_hosts)

    return probe
