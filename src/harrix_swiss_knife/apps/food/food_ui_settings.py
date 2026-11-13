"""Persist Food Tracker layout preferences in `config-temp.json`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes
from harrix_swiss_knife.apps.food.food_log_calories import (
    FOOD_LOG_COL_CALORIES,
    FOOD_LOG_COL_DATE,
    FOOD_LOG_COL_NAME_EN,
    FOOD_LOG_COL_TOTAL_PER_DAY,
    FOOD_LOG_COL_WEIGHT,
)
from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

if TYPE_CHECKING:
    from collections.abc import Sequence

FOOD_SPLITTER_SIZES_KEY = "food_log_splitter_sizes_v1"
FOOD_SPLITTER_SIZES_DEFAULT = (320, 280, 968)
EXPECTED_FOOD_SPLITTER_LEN = 3

COLUMN_VISIBILITY_KEY = "food_log_column_visibility"
FOOD_LOG_COL_NAME = 0
FOOD_LOG_COL_IS_DRINK = 1

TOGGLEABLE_COLUMNS: tuple[tuple[str, int, str], ...] = (
    ("record_id", -1, "Show record ID"),
    ("name", FOOD_LOG_COL_NAME, "Show Name"),
    ("is_drink", FOOD_LOG_COL_IS_DRINK, "Show Is Drink"),
    ("weight", FOOD_LOG_COL_WEIGHT, "Show Weight"),
    ("calories", FOOD_LOG_COL_CALORIES, "Show kcal/100g"),
    ("name_en", FOOD_LOG_COL_NAME_EN, "Show English Name"),
)
# Date / Total per day are auto-hidden while day/month grouping is on; not user toggles.
GROUPED_HIDDEN_COLUMNS: tuple[int, ...] = (FOOD_LOG_COL_DATE, FOOD_LOG_COL_TOTAL_PER_DAY)
FLAT_HIDDEN_COLUMNS: tuple[int, ...] = (FOOD_LOG_COL_TOTAL_PER_DAY,)
ALWAYS_HIDDEN_COLUMNS: tuple[int, ...] = ()
DEFAULT_COLUMN_VISIBILITY: dict[str, bool] = {key: True for key, _index, _label in TOGGLEABLE_COLUMNS}


def load_column_visibility() -> dict[str, bool]:
    """Return persisted food-log column/header visibility flags merged with defaults."""
    flags = dict(DEFAULT_COLUMN_VISIBILITY)
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return flags
    raw = config.get(COLUMN_VISIBILITY_KEY)
    if not isinstance(raw, dict):
        return flags
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, bool) and key in flags:
            flags[key] = value
    return flags


def load_food_splitter_sizes() -> list[int]:
    """Return Food-tab splitter sizes (form, items, log)."""
    return load_splitter_sizes(FOOD_SPLITTER_SIZES_KEY, FOOD_SPLITTER_SIZES_DEFAULT)


def save_column_visibility(flags: dict[str, bool]) -> dict[str, bool]:
    """Persist food-log column/header visibility flags."""
    cleaned = {key: bool(value) for key, value in flags.items() if isinstance(key, str)}
    merged = dict(DEFAULT_COLUMN_VISIBILITY)
    merged.update(cleaned)
    _ensure_temp_config()
    h.dev.config_update_value(
        COLUMN_VISIBILITY_KEY,
        merged,
        get_config_path_str(),
        is_temp=True,
    )
    return merged


def save_food_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Food-tab splitter sizes."""
    return save_splitter_sizes(FOOD_SPLITTER_SIZES_KEY, sizes, FOOD_SPLITTER_SIZES_DEFAULT)


def _ensure_temp_config() -> None:
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")
