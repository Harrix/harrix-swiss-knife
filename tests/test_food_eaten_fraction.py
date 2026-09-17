"""Tests for scaling food-log rows after eating a fraction."""

from __future__ import annotations

from harrix_swiss_knife.apps.food.eaten_fraction import (
    ATE_THIRD,
    ATE_TWO_THIRDS,
    scale_food_log_eaten_weight,
)


def test_scales_weight_only() -> None:
    """kcal/100g stays in the database; only weight changes."""
    assert scale_food_log_eaten_weight(weight=200, fraction=0.5) == 100


def test_third_fraction() -> None:
    assert scale_food_log_eaten_weight(weight=300, fraction=ATE_THIRD) == 100.0


def test_half_fraction() -> None:
    assert scale_food_log_eaten_weight(weight=120, fraction=0.5) == 60


def test_two_thirds() -> None:
    assert scale_food_log_eaten_weight(weight=90, fraction=ATE_TWO_THIRDS) == 60
