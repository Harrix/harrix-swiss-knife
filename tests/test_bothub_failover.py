"""Tests for BotHub.chat / BotHub.ru one-shot router failover."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harrix_swiss_knife.integrations.ai.bothub_failover import persist_ai_provider, prepare_bothub_router
from harrix_swiss_knife.integrations.ai.config import get_chat_provider


def _bothub_pair_config() -> dict[str, Any]:
    return {
        "ai": {"provider": "bothub", "speech_provider": ""},
        "bothub_api_key": "chat-key",
        "bothub_ru_api_key": "ru-key",
        "bothub": {"base_url": "https://bothub.chat/api/v2/openai/v1", "model": "gpt-5.5"},
        "bothub_ru": {"base_url": "https://openai.bothub.ru/v1", "model": "gpt-5.5"},
    }


def test_prepare_does_not_switch_when_current_site_is_up() -> None:
    config = _bothub_pair_config()
    persisted: list[str] = []
    switched = prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: True,
        persist=lambda provider, _speech: persisted.append(provider),
    )
    assert switched is None
    assert get_chat_provider(config) == "bothub"
    assert persisted == []


def test_prepare_switches_once_when_current_site_is_down() -> None:
    config = _bothub_pair_config()
    persisted: list[tuple[str, str | None]] = []
    switched = prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: False,
        persist=lambda provider, speech: persisted.append((provider, speech)),
    )
    assert switched == "bothub.ru"
    assert get_chat_provider(config) == "bothub.ru"
    assert persisted == [("bothub.ru", None)]


def test_prepare_does_not_switch_openai() -> None:
    config = {"ai": {"provider": "openai"}, "openai_api_key": "sk", "bothub_ru_api_key": "ru-key"}
    switched = prepare_bothub_router(config, probe=lambda _url, _proxy: False)
    assert switched is None
    assert get_chat_provider(config) == "openai"


def test_prepare_does_not_switch_without_alternate_key() -> None:
    config = _bothub_pair_config()
    config["bothub_ru_api_key"] = ""
    switched = prepare_bothub_router(config, probe=lambda _url, _proxy: False)
    assert switched is None
    assert get_chat_provider(config) == "bothub"


def test_prepare_from_bothub_ru_switches_to_bothub() -> None:
    config = _bothub_pair_config()
    config["ai"]["provider"] = "bothub.ru"
    switched = prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: False,
        persist=lambda _provider, _speech: None,
    )
    assert switched == "bothub"
    assert get_chat_provider(config) == "bothub"


def test_prepare_updates_speech_provider_when_it_is_a_bothub_router() -> None:
    config = _bothub_pair_config()
    config["ai"]["speech_provider"] = "bothub"
    persisted: list[tuple[str, str | None]] = []
    prepare_bothub_router(
        config,
        probe=lambda _url, _proxy: False,
        persist=lambda provider, speech: persisted.append((provider, speech)),
    )
    assert config["ai"]["speech_provider"] == "bothub.ru"
    assert persisted == [("bothub.ru", "bothub.ru")]


def test_persist_ai_provider_rewrites_only_ai_keys(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "editor": "cursor",
                "bothub_api_key": "snippet:api-keys/bothub-api-key.txt",
                "ai": {"provider": "bothub", "speech_provider": "", "proxy": ""},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    persist_ai_provider("bothub.ru", config_path=path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["ai"]["provider"] == "bothub.ru"
    assert data["ai"]["speech_provider"] == ""
    assert data["bothub_api_key"] == "snippet:api-keys/bothub-api-key.txt"
    assert data["editor"] == "cursor"
