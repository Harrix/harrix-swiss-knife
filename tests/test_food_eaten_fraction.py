"""Tests for scaling food-log rows after eating a fraction."""

from __future__ import annotations

import pytest

from harrix_swiss_knife.apps.food.eaten_fraction import (
    ATE_THIRD,
    ATE_TWO_THIRDS,
    scale_food_log_eaten_amounts,
)


def test_weight_mode_scales_only_mass() -> None:
    """Calories per 100 g stay in the database; only weight changes."""
    weight, portion = scale_food_log_eaten_amounts(
        weight=200,
        portion_calories=None,
        fraction=0.5,
    )
    assert weight == 100
    assert portion is None


def test_portion_mode_scales_mass_and_serving_calories() -> None:
    """A serving-calorie row scales both weight and portion calories."""
    weight, portion = scale_food_log_eaten_amounts(
        weight=300,
        portion_calories=450,
        fraction=ATE_THIRD,
    )
    assert weight == pytest.approx(100.0)
    assert portion == pytest.approx(150.0)


def test_portion_mode_wins_when_portion_calories_are_set() -> None:
    """Positive portion calories mean serving mode."""
    weight, portion = scale_food_log_eaten_amounts(
        weight=120,
        portion_calories=240,
        fraction=0.5,
    )
    assert weight == 60
    assert portion == 120


def test_two_thirds_scales_weight_mode() -> None:
    """Two thirds of 90 g is 60 g."""
    weight, portion = scale_food_log_eaten_amounts(
        weight=90,
        portion_calories=0,
        fraction=ATE_TWO_THIRDS,
    )
    assert weight == 60
    assert portion == 0
