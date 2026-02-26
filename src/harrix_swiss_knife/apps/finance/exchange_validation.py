"""Exchange data validation for finance app.

Centralized validation rules for currency exchange (form and table auto-save)
so that main window, edit dialog, and mixins share the same logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def validate_exchange_data(
    from_currency: str,
    to_currency: str,
    amount_from: float,
    amount_to: float,
    rate: float,
    fee: float,
    *,
    date_str: str | None = None,
    is_valid_date: Callable[[str], bool] | None = None,
) -> list[str]:
    """Validate exchange fields; return list of error messages (empty if valid).

    Args:

    - `from_currency` (`str`): From currency code.
    - `to_currency` (`str`): To currency code.
    - `amount_from` (`float`): Amount in source currency.
    - `amount_to` (`float`): Amount in target currency.
    - `rate` (`float`): Exchange rate.
    - `fee` (`float`): Fee amount.
    - `date_str` (`str | None`): Optional date string to validate (YYYY-MM-DD).
    - `is_valid_date` (`Callable[[str], bool] | None`): Optional date validator.

    Returns:

    - `list[str]`: Error messages; empty list if valid.

    """
    errors: list[str] = []

    if not (from_currency or "").strip() or not (to_currency or "").strip():
        errors.append("Currency codes cannot be empty")
    elif from_currency.strip() == to_currency.strip():
        errors.append("From and To currencies must be different")

    if amount_from < 0:
        errors.append("Amount From cannot be negative")
    if amount_to < 0:
        errors.append("Amount To cannot be negative")
    if rate <= 0:
        errors.append("Exchange rate must be positive")
    if fee < 0:
        errors.append("Fee cannot be negative")

    if date_str is not None and is_valid_date is not None and not is_valid_date(date_str):
        errors.append(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

    return errors
