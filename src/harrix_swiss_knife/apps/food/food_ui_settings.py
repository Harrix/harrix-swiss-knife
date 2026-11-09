"""Persist Food Tracker layout preferences in `config-temp.json`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes

if TYPE_CHECKING:
    from collections.abc import Sequence

FOOD_SPLITTER_SIZES_KEY = "food_log_splitter_sizes_v1"
FOOD_SPLITTER_SIZES_DEFAULT = (320, 280, 968)
EXPECTED_FOOD_SPLITTER_LEN = 3


def load_food_splitter_sizes() -> list[int]:
    """Return Food-tab splitter sizes (form, items, log)."""
    return load_splitter_sizes(FOOD_SPLITTER_SIZES_KEY, FOOD_SPLITTER_SIZES_DEFAULT)


def save_food_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Food-tab splitter sizes."""
    return save_splitter_sizes(FOOD_SPLITTER_SIZES_KEY, sizes, FOOD_SPLITTER_SIZES_DEFAULT)
