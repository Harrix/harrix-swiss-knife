"""Total accounts balance and per-currency detail lines for the finance UI."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.finance.transaction_helpers import convert_currency_amount as convert_currency

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager


def format_total_accounts_balance_details(db_manager: DatabaseManager) -> tuple[float, str]:
    """Compute total balance in default currency and formatted per-currency lines.

    Returns:

    - `tuple[float, str]`: Total in default currency and multi-line detail text.

    """
    try:
        total_balance: float = db_manager.get_total_accounts_balance_in_currency(None)

        default_currency_code: str = db_manager.get_default_currency()
        default_currency_info = db_manager.get_currency_by_code(default_currency_code)
        if not default_currency_info:
            return total_balance, "Default currency not found"

        default_currency_id: int = default_currency_info[0]
        default_currency_symbol: str = default_currency_info[2]
        db_manager.get_currency_subdivision(default_currency_id)

        accounts_data: list = db_manager.get_all_accounts()

        today: str = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")

        currency_balances: dict[str, float] = {}

        for account in accounts_data:
            _account_id, _account_name, balance_minor_units, currency_code, _is_liquid, _is_cash, currency_id = account

            balance_major_units: float = db_manager.convert_from_minor_units(balance_minor_units, currency_id)

            if currency_balances.get(currency_code) is None:
                currency_balances[currency_code] = 0.0
            currency_balances[currency_code] += balance_major_units

        details_lines: list[str] = []
        for currency_code, balance in currency_balances.items():
            if currency_code == default_currency_code:
                details_lines.append(f"{currency_code}: {balance:,.2f}{default_currency_symbol}")
            else:
                currency_info = db_manager.get_currency_by_id(db_manager.get_currency_by_code(currency_code)[0])
                currency_symbol: str = currency_info[2] if currency_info else currency_code

                currency_id: int = db_manager.get_currency_by_code(currency_code)[0]
                converted_amount: float = convert_currency(balance, currency_id, default_currency_id, db_manager, today)

                if converted_amount == balance and currency_id != default_currency_id:
                    details_lines.append(f"{currency_code}: {balance:,.2f}{currency_symbol} (exchange rate not found)")
                else:
                    details_lines.append(
                        f"{currency_code}: {balance:,.2f}{currency_symbol} → "
                        f"{converted_amount:,.2f}{default_currency_symbol}"
                    )

        details_text: str = "\n".join(details_lines)

    except Exception as e:
        print(f"Error calculating total accounts balance: {e}")
        return 0.0, f"Error: {e!s}"
    else:
        return total_balance, details_text
