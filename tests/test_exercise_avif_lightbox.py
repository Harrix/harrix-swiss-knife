"""Tests for exercise AVIF lightbox helpers."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.widgets.exercise_avif_lightbox import parse_speed_text


def test_parse_speed_text() -> None:
    assert parse_speed_text("1.25") == 1.25
    assert parse_speed_text(" 0,5x ") == 0.5
    assert parse_speed_text("2X") == 2.0
    assert parse_speed_text("") is None
    assert parse_speed_text("fast") is None
