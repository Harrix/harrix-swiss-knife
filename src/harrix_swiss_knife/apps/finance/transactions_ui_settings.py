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
EXPECTED_SPLITTER_LEN = 3


def load_column_visibility() -> dict[str, bool]:
    """Return persisted column/header visibility flags."""
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return {}
    raw = config.get(COLUMN_VISIBILITY_KEY)
    if not isinstance(raw, dict):
        return {}
    return {key: value for key, value in raw.items() if isinstance(key, str) and isinstance(value, bool)}


def load_splitter_sizes() -> list[int]:
    """Return Transactions-tab splitter sizes (form, categories, table)."""
    return _load_int_list(SPLITTER_SIZES_KEY, list(SPLITTER_SIZES_DEFAULT), expected_len=EXPECTED_SPLITTER_LEN)


def save_column_visibility(flags: dict[str, bool]) -> dict[str, bool]:
    """Persist column/header visibility flags."""
    cleaned = {key: bool(value) for key, value in flags.items() if isinstance(key, str)}
    _ensure_temp_config()
    h.dev.config_update_value(
        COLUMN_VISIBILITY_KEY,
        cleaned,
        get_config_path_str(),
        is_temp=True,
    )
    return cleaned


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
