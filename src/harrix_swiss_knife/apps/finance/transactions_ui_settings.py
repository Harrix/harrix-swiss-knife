"""Persist Finance Transactions-tab layout preferences in `config-temp.json`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

if TYPE_CHECKING:
    from collections.abc import Sequence

# v2 defaults: narrower form (~320), steadier categories (~290), table gets the rest.
SPLITTER_SIZES_KEY = "finance_transactions_splitter_sizes_v2"
COLUMN_VISIBILITY_KEY = "finance_transactions_column_visibility"
SPLITTER_SIZES_DEFAULT = (320, 290, 958)
# Logical column indices in `tableView_transactions` (Description=0 … Total=7).
OPTIONAL_COLUMN_ENGLISH = 1
TRANSACTION_COL_DESCRIPTION = 0
TRANSACTION_COL_ENGLISH = 1
TRANSACTION_COL_AMOUNT = 2
TRANSACTION_COL_CATEGORY = 3
TRANSACTION_COL_CURRENCY = 4
TRANSACTION_COL_DATE = 5
TRANSACTION_COL_TAG = 6
TRANSACTION_COL_TOTAL_PER_DAY = 7
EXPECTED_SPLITTER_LEN = 3

# Ordinary columns the user may toggle. Total per day stays hidden (lives in day
# headers). Date stays hidden while day/month grouping is on; filtered views show it.
# Description stays visible: day headers paint through that column when spanned.
TOGGLEABLE_COLUMNS: tuple[tuple[str, int, str], ...] = (
    ("record_id", -1, "Show record ID"),
    ("english", TRANSACTION_COL_ENGLISH, "Show English"),
    ("amount", TRANSACTION_COL_AMOUNT, "Show Amount"),
    ("category", TRANSACTION_COL_CATEGORY, "Show Category"),
    ("currency", TRANSACTION_COL_CURRENCY, "Show Currency"),
    ("tag", TRANSACTION_COL_TAG, "Show Tag"),
)
# Hidden whenever day/month grouping is active. Filtered (flat) mode shows Date.
GROUPED_HIDDEN_COLUMNS: tuple[int, ...] = (TRANSACTION_COL_DATE, TRANSACTION_COL_TOTAL_PER_DAY)
# Always hidden — day totals are only shown in group banners.
ALWAYS_HIDDEN_COLUMNS: tuple[int, ...] = (TRANSACTION_COL_TOTAL_PER_DAY,)
DEFAULT_COLUMN_VISIBILITY: dict[str, bool] = {key: True for key, _index, _label in TOGGLEABLE_COLUMNS}


def load_column_visibility() -> dict[str, bool]:
    """Return persisted column/header visibility flags merged with defaults."""
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


def load_splitter_sizes() -> list[int]:
    """Return Transactions-tab splitter sizes (form, categories, table)."""
    return _load_int_list(SPLITTER_SIZES_KEY, list(SPLITTER_SIZES_DEFAULT), expected_len=EXPECTED_SPLITTER_LEN)


def save_column_visibility(flags: dict[str, bool]) -> dict[str, bool]:
    """Persist column/header visibility flags."""
    cleaned = {key: bool(value) for key, value in flags.items() if isinstance(key, str)}
    # Keep unknown keys (forward-compatible) but always store known defaults too.
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


def save_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Transactions-tab splitter sizes."""
    cleaned = _clean_positive_ints(sizes, expected_len=EXPECTED_SPLITTER_LEN, fallback=list(SPLITTER_SIZES_DEFAULT))
    _ensure_temp_config()
    h.dev.config_update_value(
        SPLITTER_SIZES_KEY,
        cleaned,
        get_config_path_str(),
        is_temp=True,
    )
    return cleaned


def _clean_positive_ints(raw: Sequence[object], *, expected_len: int, fallback: list[int]) -> list[int]:
    cleaned: list[int] = []
    for item in raw:
        if isinstance(item, bool):
            return list(fallback)
        if isinstance(item, int):
            number = item
        elif isinstance(item, float):
            number = int(item)
        elif isinstance(item, str):
            try:
                number = int(item.strip())
            except ValueError:
                return list(fallback)
        else:
            return list(fallback)
        if number <= 0:
            return list(fallback)
        cleaned.append(number)
    if len(cleaned) != expected_len:
        return list(fallback)
    return cleaned


def _ensure_temp_config() -> None:
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")


def _load_int_list(key: str, fallback: list[int], *, expected_len: int) -> list[int]:
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return list(fallback)
    raw = config.get(key)
    if not isinstance(raw, list):
        return list(fallback)
    return _clean_positive_ints(raw, expected_len=expected_len, fallback=fallback)
