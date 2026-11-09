"""Persist tracker multi-column splitter sizes in `config-temp.json`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

if TYPE_CHECKING:
    from collections.abc import Sequence


def clean_positive_ints(raw: Sequence[object], *, expected_len: int, fallback: list[int]) -> list[int]:
    """Return `expected_len` positive ints, or `fallback` when parsing fails."""
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


def load_splitter_sizes(key: str, default: Sequence[int]) -> list[int]:
    """Return persisted positive splitter sizes for `key`, or `default`."""
    fallback = list(default)
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return fallback
    raw = config.get(key)
    if not isinstance(raw, list):
        return fallback
    return clean_positive_ints(raw, expected_len=len(fallback), fallback=fallback)


def save_splitter_sizes(key: str, sizes: Sequence[int], default: Sequence[int]) -> list[int]:
    """Persist positive splitter sizes for `key`."""
    fallback = list(default)
    cleaned = clean_positive_ints(sizes, expected_len=len(fallback), fallback=fallback)
    _ensure_temp_config()
    h.dev.config_update_value(key, cleaned, get_config_path_str(), is_temp=True)
    return cleaned


def _ensure_temp_config() -> None:
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")
