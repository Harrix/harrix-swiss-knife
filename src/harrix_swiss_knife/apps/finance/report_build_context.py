"""Shared preload context for finance report generation."""

from __future__ import annotations

from dataclasses import dataclass

from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager
from harrix_swiss_knife.apps.finance.services.exchange_rates import PreloadedExchangeRates


@dataclass(frozen=True, slots=True)
class ReportBuildContext:
    """Preloaded database state for building finance reports off the UI thread."""

    db_manager: DatabaseManager
    currency_id: int
    rates: PreloadedExchangeRates
    currencies_by_code: dict[str, tuple[int, str, str]]
    currencies_by_id: dict[int, tuple[str, str, str]]

    @classmethod
    def load(cls, db_filename: str) -> ReportBuildContext:
        """Open the database and preload currencies and exchange rates."""
        db_manager = DatabaseManager(db_filename)
        currencies_by_code, currencies_by_id = db_manager.get_all_currencies_map()
        return cls(
            db_manager=db_manager,
            currency_id=db_manager.get_default_currency_id(),
            rates=db_manager.exchange_rates.preload_all_rates(),
            currencies_by_code=currencies_by_code,
            currencies_by_id=currencies_by_id,
        )
