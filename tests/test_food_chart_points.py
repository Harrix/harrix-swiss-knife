"""Tests for food chart points that skip empty days."""

from __future__ import annotations

from datetime import UTC, datetime

from harrix_swiss_knife.apps.food.mixins import has_period_gap, iter_nonempty_chart_segments


def _dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=UTC)


def test_has_period_gap_for_days_months_and_years() -> None:
    day = _dt(2024, 1, 1)
    next_day = _dt(2024, 1, 2)
    skipped_day = _dt(2024, 1, 4)
    assert not has_period_gap(day, next_day, "Days")
    assert has_period_gap(day, skipped_day, "Days")
    assert not has_period_gap(_dt(2024, 1, 1), _dt(2024, 2, 1), "Months")
    assert has_period_gap(_dt(2024, 1, 1), _dt(2024, 3, 1), "Months")
    assert not has_period_gap(_dt(2024, 1, 1), _dt(2025, 1, 1), "Years")
    assert has_period_gap(_dt(2024, 1, 1), _dt(2026, 1, 1), "Years")


def test_iter_nonempty_chart_segments_skips_zeros_and_breaks_gaps() -> None:
    x_values = [
        _dt(2024, 1, 1),
        _dt(2024, 1, 2),
        _dt(2024, 1, 3),
        _dt(2024, 1, 10),
        _dt(2024, 1, 11),
    ]
    y_values = [1800, 0, 2100, 2500, None]
    segments = iter_nonempty_chart_segments(x_values, y_values, "Days")
    assert len(segments) == 3
    assert segments[0] == ([_dt(2024, 1, 1)], [1800])
    assert segments[1] == ([_dt(2024, 1, 3)], [2100])
    assert segments[2] == ([_dt(2024, 1, 10)], [2500])
