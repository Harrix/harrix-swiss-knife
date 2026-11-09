"""Persist Finance non-Transactions splitter sizes in `config-temp.json`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes

if TYPE_CHECKING:
    from collections.abc import Sequence

ACCOUNTS_SPLITTER_KEY = "finance_accounts_splitter_sizes_v1"
ACCOUNTS_SPLITTER_DEFAULT = (300, 1268)
EXCHANGE_SPLITTER_KEY = "finance_exchange_splitter_sizes_v1"
EXCHANGE_SPLITTER_DEFAULT = (340, 1228)
RATES_SPLITTER_KEY = "finance_rates_splitter_sizes_v1"
RATES_SPLITTER_DEFAULT = (420, 1148)
CHARTS_SPLITTER_KEY = "finance_charts_splitter_sizes_v1"
CHARTS_SPLITTER_DEFAULT = (320, 1248)
REPORTS_SPLITTER_KEY = "finance_reports_splitter_sizes_v1"
REPORTS_SPLITTER_DEFAULT = (300, 1268)


def load_accounts_splitter_sizes() -> list[int]:
    """Return Accounts-tab splitter sizes."""
    return load_splitter_sizes(ACCOUNTS_SPLITTER_KEY, ACCOUNTS_SPLITTER_DEFAULT)


def load_charts_splitter_sizes() -> list[int]:
    """Return Charts-tab splitter sizes."""
    return load_splitter_sizes(CHARTS_SPLITTER_KEY, CHARTS_SPLITTER_DEFAULT)


def load_exchange_splitter_sizes() -> list[int]:
    """Return Currency Exchange-tab splitter sizes."""
    return load_splitter_sizes(EXCHANGE_SPLITTER_KEY, EXCHANGE_SPLITTER_DEFAULT)


def load_rates_splitter_sizes() -> list[int]:
    """Return Exchange Rates-tab splitter sizes."""
    return load_splitter_sizes(RATES_SPLITTER_KEY, RATES_SPLITTER_DEFAULT)


def load_reports_splitter_sizes() -> list[int]:
    """Return Reports-tab splitter sizes."""
    return load_splitter_sizes(REPORTS_SPLITTER_KEY, REPORTS_SPLITTER_DEFAULT)


def save_accounts_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Accounts-tab splitter sizes."""
    return save_splitter_sizes(ACCOUNTS_SPLITTER_KEY, sizes, ACCOUNTS_SPLITTER_DEFAULT)


def save_charts_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Charts-tab splitter sizes."""
    return save_splitter_sizes(CHARTS_SPLITTER_KEY, sizes, CHARTS_SPLITTER_DEFAULT)


def save_exchange_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Currency Exchange-tab splitter sizes."""
    return save_splitter_sizes(EXCHANGE_SPLITTER_KEY, sizes, EXCHANGE_SPLITTER_DEFAULT)


def save_rates_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Exchange Rates-tab splitter sizes."""
    return save_splitter_sizes(RATES_SPLITTER_KEY, sizes, RATES_SPLITTER_DEFAULT)


def save_reports_splitter_sizes(sizes: Sequence[int]) -> list[int]:
    """Persist Reports-tab splitter sizes."""
    return save_splitter_sizes(REPORTS_SPLITTER_KEY, sizes, REPORTS_SPLITTER_DEFAULT)
