"""Tests for exercise progress math (no database)."""

from __future__ import annotations

from unittest.mock import MagicMock

from harrix_swiss_knife.apps.fitness.progress_calculator import ExerciseProgressCalculator


def test_calculate_daily_needed_exact_division() -> None:
    calc = ExerciseProgressCalculator(MagicMock())
    inc, max_only = calc.calculate_daily_needed(100, 5, 10)
    assert inc == 10
    assert max_only == 20


def test_calculate_daily_needed_ceils_fractional() -> None:
    calc = ExerciseProgressCalculator(MagicMock())
    inc, max_only = calc.calculate_daily_needed(101, 3, 10)
    assert inc == 11
    assert max_only == 34


def test_calculate_daily_needed_zero_divisors() -> None:
    calc = ExerciseProgressCalculator(MagicMock())
    assert calc.calculate_daily_needed(50, 0, 0) == (0.0, 0.0)
    assert calc.calculate_daily_needed(50, 0, 5) == (10.0, 0.0)
    assert calc.calculate_daily_needed(50, 4, 0) == (0.0, 13.0)
