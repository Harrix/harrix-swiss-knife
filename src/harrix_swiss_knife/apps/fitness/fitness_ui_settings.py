"""Persist Fitness Tracker layout preferences in `config-temp.json`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes
from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

if TYPE_CHECKING:
    from collections.abc import Sequence

SETS_SPLITTER_SIZES_KEY = "fitness_sets_splitter_sizes_v1"
SETS_SPLITTER_SIZES_DEFAULT = (320, 340, 908)
EXPECTED_SETS_SPLITTER_LEN = 3

COLUMN_VISIBILITY_KEY = "fitness_process_column_visibility"
PROCESS_COL_EXERCISE = 0
PROCESS_COL_TYPE = 1
PROCESS_COL_QUANTITY = 2
PROCESS_COL_DATE = 3

TOGGLEABLE_COLUMNS: tuple[tuple[str, int, str], ...] = (
    ("record_id", -1, "Show record ID"),
    ("exercise", PROCESS_COL_EXERCISE, "Show Exercise"),
    ("exercise_type", PROCESS_COL_TYPE, "Show Exercise Type"),
    ("quantity", PROCESS_COL_QUANTITY, "Show Quantity"),
)
# Date is auto-hidden while day/month grouping is on; not a user toggle.
GROUPED_HIDDEN_COLUMNS: tuple[int, ...] = (PROCESS_COL_DATE,)
ALWAYS_HIDDEN_COLUMNS: tuple[int, ...] = ()
DEFAULT_COLUMN_VISIBILITY: dict[str, bool] = {key: True for key, _index, _label in TOGGLEABLE_COLUMNS}


def load_column_visibility() -> dict[str, bool]:
    """Return persisted process column/header visibility flags merged with defaults."""
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


def load_sets_splitter_sizes() -> list[int]:
    """Return Sets-tab splitter sizes (form, exercises, process)."""
    return load_splitter_sizes(SETS_SPLITTER_SIZES_KEY, SETS_SPLITTER_SIZES_DEFAULT)


def save_column_visibility(flags: dict[str, bool]) -> dict[str, bool]:
    """Persist process column/header visibility flags."""
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


def save_sets_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Sets-tab splitter sizes."""
    return save_splitter_sizes(SETS_SPLITTER_SIZES_KEY, sizes, SETS_SPLITTER_SIZES_DEFAULT)


def _ensure_temp_config() -> None:
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")
