"""Tests for screen recording helpers."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QRect

from harrix_swiss_knife.screen_record.config import (
    DEFAULT_SCREEN_RECORD_AUDIO,
    DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS,
    get_screen_record_audio,
    get_screen_record_countdown_seconds,
    get_screen_record_microphone_id,
)
from harrix_swiss_knife.screen_record.geometry import even_size
from harrix_swiss_knife.screen_record.record_frame import hit_test_record_frame_handle
from harrix_swiss_knife.screen_record.session import videos_folder


def test_even_size_rounds_down_to_even() -> None:
    assert even_size(101, 50) == (100, 50)
    assert even_size(2, 2) == (2, 2)
    assert even_size(1, 1) == (2, 2)


def test_screen_record_config_defaults() -> None:
    assert get_screen_record_audio({}) == DEFAULT_SCREEN_RECORD_AUDIO
    assert get_screen_record_countdown_seconds({}) == DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS
    assert get_screen_record_audio({"screen_record_audio": "mic"}) == "mic"
    assert get_screen_record_audio({"screen_record_audio": "nope"}) == DEFAULT_SCREEN_RECORD_AUDIO
    assert get_screen_record_countdown_seconds({"apps": {"screen_record_countdown_seconds": 5}}) == 5
    assert get_screen_record_countdown_seconds({"apps": {"screen_record_countdown_seconds": 99}}) == 30
    assert get_screen_record_microphone_id({}) == ""
    assert get_screen_record_microphone_id({"apps": {"screen_record_microphone_id": "abc"}}) == "abc"


def test_videos_folder(tmp_path: Path) -> None:
    folder = videos_folder(tmp_path)
    assert folder == tmp_path / "temp" / "videos"


def test_record_frame_top_left_handle_moves_region() -> None:
    rect = QRect(40, 30, 120, 80)
    assert hit_test_record_frame_handle(rect, QPoint(40, 30)) == "move"
    assert hit_test_record_frame_handle(rect, QPoint(36, 26)) == "move"
    assert hit_test_record_frame_handle(rect, QPoint(159, 109)) == "se"
    assert hit_test_record_frame_handle(rect, QPoint(100, 30)) == "n"
