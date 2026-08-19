"""Tests for toast elapsed clock formatting."""

from __future__ import annotations

import pytest

from harrix_swiss_knife.toast_countdown_notification import format_elapsed_clock


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "00:00"),
        (23, "00:23"),
        (75, "01:15"),
        (3599, "59:59"),
        (3600, "01:00:00"),
        (3661, "01:01:01"),
    ],
)
def test_format_elapsed_clock(seconds: int, expected: str) -> None:
    assert format_elapsed_clock(seconds) == expected


def test_format_elapsed_clock_clamps_negative() -> None:
    assert format_elapsed_clock(-5) == "00:00"
