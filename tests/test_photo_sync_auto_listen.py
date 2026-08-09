"""Tests for Photo Sync credentials, session progress, and auto-listen gates."""

from __future__ import annotations

import json
from pathlib import Path

from harrix_swiss_knife.photo_sync.auto_listen import maybe_start_auto_listen
from harrix_swiss_knife.photo_sync.server import PhotoSyncServer, SyncStats
from harrix_swiss_knife.photo_sync.settings import (
    load_saved_credentials,
    persist_credentials,
    photos_dir_from_config,
)

_TEST_TOKEN = "saved-token-value"  # noqa: S105
_TEST_TOKEN_SHORT = "tok"  # noqa: S105


def test_server_reuses_injected_credentials(tmp_path: Path) -> None:
    server = PhotoSyncServer(
        tmp_path,
        token=_TEST_TOKEN,
        confirm_code="42",
    )
    assert server.token == _TEST_TOKEN
    assert server.confirm_code == "42"


def test_server_mints_credentials_when_missing(tmp_path: Path) -> None:
    server = PhotoSyncServer(tmp_path, token="", confirm_code="  ")
    assert server.token
    assert len(server.confirm_code) == 2
    assert server.confirm_code.isdigit()


def test_session_progress_counts_uploads() -> None:
    stats = SyncStats()
    stats.begin_session(3)
    assert stats.session_active
    assert stats.session_in_progress
    stats.record_session_item()
    stats.record_session_item()
    assert stats.session_done == 2
    assert stats.session_in_progress
    stats.record_session_item()
    assert stats.session_done == 3
    assert not stats.session_in_progress
    assert not stats.session_active


def test_empty_manifest_session_is_inactive() -> None:
    stats = SyncStats()
    stats.begin_session(0)
    assert stats.session_total == 0
    assert not stats.session_active
    assert not stats.session_in_progress


def test_load_and_persist_credentials(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    persist_credentials(config_path, token=_TEST_TOKEN_SHORT, confirm_code="17")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["photo_sync_token"] == _TEST_TOKEN_SHORT
    assert data["photo_sync_confirm_code"] == "17"
    loaded = load_saved_credentials(data)
    assert loaded == (_TEST_TOKEN_SHORT, "17")


def test_photos_dir_from_config(tmp_path: Path) -> None:
    assert photos_dir_from_config({}) is None
    assert photos_dir_from_config({"path_photos": str(tmp_path / "missing")}) is None
    assert photos_dir_from_config({"path_photos": str(tmp_path)}) == tmp_path.resolve()


def test_maybe_start_auto_listen_noop_without_credentials(tmp_path: Path) -> None:
    assert (
        maybe_start_auto_listen(
            {
                "photo_sync_auto_listen": True,
                "path_photos": str(tmp_path),
            },
        )
        is False
    )


def test_maybe_start_auto_listen_noop_when_disabled(tmp_path: Path) -> None:
    assert (
        maybe_start_auto_listen(
            {
                "photo_sync_auto_listen": False,
                "path_photos": str(tmp_path),
                "photo_sync_token": _TEST_TOKEN_SHORT,
                "photo_sync_confirm_code": "42",
            },
        )
        is False
    )
