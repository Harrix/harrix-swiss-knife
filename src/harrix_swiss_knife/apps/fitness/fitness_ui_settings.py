"""Persist Fitness Tracker layout preferences in `config-temp.json`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes

if TYPE_CHECKING:
    from collections.abc import Sequence

SETS_SPLITTER_SIZES_KEY = "fitness_sets_splitter_sizes_v1"
SETS_SPLITTER_SIZES_DEFAULT = (320, 340, 908)
EXPECTED_SETS_SPLITTER_LEN = 3


def load_sets_splitter_sizes() -> list[int]:
    """Return Sets-tab splitter sizes (form, exercises, process)."""
    return load_splitter_sizes(SETS_SPLITTER_SIZES_KEY, SETS_SPLITTER_SIZES_DEFAULT)


def save_sets_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Sets-tab splitter sizes."""
    return save_splitter_sizes(SETS_SPLITTER_SIZES_KEY, sizes, SETS_SPLITTER_SIZES_DEFAULT)
