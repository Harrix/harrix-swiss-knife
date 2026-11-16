"""Shared FX date limits and yfinance log noise control."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta

_YFINANCE_LOGGERS: tuple[str, ...] = (
    "yfinance",
    "yfinance.base",
    "yfinance.data",
    "yfinance.scrapers",
    "yfinance.utils",
)


def configure_yfinance_logging() -> None:
    """Silence yfinance WARNING/ERROR spam (SSL crumb, empty history / delisted)."""
    for name in _YFINANCE_LOGGERS:
        logging.getLogger(name).setLevel(logging.CRITICAL)


def dates_through_closed_fx_day(dates: list[str], *, now: datetime | None = None) -> list[str]:
    """Drop today/future dates that yfinance often returns empty for."""
    cutoff = latest_closed_fx_date(now=now).strftime("%Y-%m-%d")
    return [day for day in dates if day <= cutoff]


def latest_closed_fx_date(*, now: datetime | None = None) -> date:
    """Return yesterday in local time — the latest day Yahoo daily FX bars are reliable."""
    current = (now or datetime.now(UTC).astimezone()).date()
    return current - timedelta(days=1)
