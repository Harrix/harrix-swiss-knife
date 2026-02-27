"""Pure calculation and transformation helpers for finance transaction data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager

# Minimum row length for get_filtered_transactions / get_all_transactions (up to category_type index 7)
MIN_TRANSACTION_ROW_LENGTH = 8


def calculate_daily_expenses(rows: list[list[Any]], db_manager: DatabaseManager | None) -> dict[str, float]:
    """Calculate daily expenses from transaction data.

    Args:

    - `rows` (`list[list[Any]]`): Raw transaction data from database.
    - `db_manager` (`DatabaseManager | None`): Database manager for currency conversion.

    Returns:

    - `dict[str, float]`: Dictionary mapping dates to total expenses for that day.

    """
    daily_expenses: dict[str, float] = {}

    for row in rows:
        amount_cents: int = row[1]
        date: str = row[5]
        category_type: int = row[7]

        # Only count expenses (category_type == 0)
        if category_type == 0:
            currency_code: str = row[4]
            amount: float
            if db_manager:
                currency_info = db_manager.get_currency_by_code(currency_code)
                currency_id: int = currency_info[0] if currency_info else 1
                amount = db_manager.convert_from_minor_units(amount_cents, currency_id)
            else:
                amount = float(amount_cents) / 100  # Fallback

            if date in daily_expenses:
                daily_expenses[date] += amount
            else:
                daily_expenses[date] = amount

    return daily_expenses


def calculate_exchange_loss(
    from_currency_id: int,
    to_currency_id: int,
    amount_from: float,
    amount_to: float,
    default_currency_id: int | None,
    db_manager: DatabaseManager | None,
    fee: float = 0.0,
    use_date: str | None = None,
) -> float:
    """Calculate loss due to exchange rate difference.

    Args:

    - `from_currency_id` (`int`): Source currency ID.
    - `to_currency_id` (`int`): Target currency ID.
    - `amount_from` (`float`): Amount in source currency.
    - `amount_to` (`float`): Amount in target currency.
    - `default_currency_id` (`int | None`): Default currency ID for conversion.
    - `db_manager` (`DatabaseManager | None`): Database manager for rates.
    - `fee` (`float`): Exchange fee in source currency.
    - `use_date` (`str | None`): Date to use for rate calculation. If None, uses today.

    Returns:

    - `float`: Loss amount in default currency (negative = loss, positive = profit).

    """
    if db_manager is None:
        return 0.0
    try:
        target_date: str = (
            use_date if use_date is not None else datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        )

        rate_to_per_from: float = db_manager.get_exchange_rate(from_currency_id, to_currency_id, target_date)

        if rate_to_per_from == 1.0 and from_currency_id != to_currency_id and use_date is None:
            rate_to_per_from = db_manager.get_exchange_rate(from_currency_id, to_currency_id)

        loss_in_from_currency: float = calculate_exchange_loss_in_source_currency(
            amount_from, amount_to, rate_to_per_from, fee
        )

        if default_currency_id is not None and from_currency_id != default_currency_id:
            today: str = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
            return convert_currency_amount(
                loss_in_from_currency, from_currency_id, default_currency_id, db_manager, today
            )
        result = loss_in_from_currency
    except Exception as e:
        date_info = f"date {use_date}" if use_date else "today"
        print(f"Error calculating exchange loss for {date_info}: {e}")
        return 0.0

    return result


def calculate_exchange_loss_in_source_currency(
    amount_from: float,
    amount_to: float,
    rate_to_per_from: float,
    fee: float = 0.0,
) -> float:
    """Calculate exchange loss in source currency using given rate.

    Args:

    - `amount_from` (`float`): Amount in source currency.
    - `amount_to` (`float`): Amount in target currency.
    - `rate_to_per_from` (`float`): Exchange rate (to per 1 from).
    - `fee` (`float`): Exchange fee in source currency.

    Returns:

    - `float`: Loss amount in source currency (negative = loss, positive = profit).

    """
    try:
        if rate_to_per_from and rate_to_per_from != 0:
            expected_from: float = amount_to / rate_to_per_from
            total_cost: float = amount_from + fee
            diff_from: float = total_cost - expected_from
            return -diff_from
    except Exception as e:
        print(f"Error calculating exchange loss in source currency: {e}")
    return 0.0


def convert_currency_amount(
    amount: float,
    from_currency_id: int,
    to_currency_id: int,
    db_manager: DatabaseManager | None,
    date: str | None = None,
) -> float:
    """Convert amount from one currency to another.

    Args:

    - `amount` (`float`): Amount to convert.
    - `from_currency_id` (`int`): Source currency ID.
    - `to_currency_id` (`int`): Target currency ID.
    - `db_manager` (`DatabaseManager | None`): Database manager for rate lookup.
    - `date` (`str | None`): Date for rate lookup (uses today if None).

    Returns:

    - `float`: Converted amount in target currency.

    """
    if db_manager is None:
        return amount
    try:
        if from_currency_id == to_currency_id:
            return amount

        if date is None:
            date = datetime.now(UTC).astimezone().strftime("%Y-%m-%d")

        rate: float = db_manager.get_exchange_rate(from_currency_id, to_currency_id, date)
        if rate == 1.0 and from_currency_id != to_currency_id:
            rate = db_manager.get_exchange_rate(from_currency_id, to_currency_id)

        if rate and rate != 0:
            return amount * rate
    except Exception as e:
        print(f"Error converting currency amount: {e}")
    return amount


def transaction_money_op_value(
    row: list[Any],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> float:
    """Return signed monetary operation value for one transaction row in target currency.

    Expense (category type 0) is negative, income (type 1) is positive.
    Uses exchange rate at transaction date. If target_currency_id is None, uses
    default currency from settings.

    Row format: same as get_filtered_transactions / get_all_transactions:
    [t._id, t.amount, description, cat.name, c.code, t.date, t.tag, cat.type, cat.icon, c.symbol].

    Args:

    - `row` (`list[Any]`): One transaction row (at least 8 elements).
    - `db_manager` (`DatabaseManager | None`): Database manager for rates and default currency.
    - `target_currency_id` (`int | None`): Target currency ID. None = default currency.

    Returns:

    - `float`: Signed amount in target currency (major units).

    """
    if db_manager is None or len(row) < MIN_TRANSACTION_ROW_LENGTH:
        return 0.0
    try:
        amount_minor: int = row[1]
        currency_code: str = row[4]
        transaction_date: str = row[5]
        category_type: int = row[7]

        if target_currency_id is None:
            target_currency_id = db_manager.get_default_currency_id()

        currency_info = db_manager.get_currency_by_code(currency_code)
        source_currency_id: int = currency_info[0] if currency_info else 1
        amount_major: float = db_manager.convert_from_minor_units(amount_minor, source_currency_id)
        converted: float = convert_currency_amount(
            amount_major, source_currency_id, target_currency_id, db_manager, transaction_date
        )
        sign: int = -1 if category_type == 0 else 1
        return sign * converted
    except Exception as e:
        print(f"Error computing transaction money op value: {e}")
        return 0.0


def transform_transaction_data(
    rows: list[list[Any]],
    daily_expenses: dict[str, float],
    date_colors: list[Any],
    db_manager: DatabaseManager | None,
) -> list[list[Any]]:
    """Transform transaction data for display with colors and daily totals.

    Args:

    - `rows` (`list[list[Any]]`): Raw transaction data.
    - `daily_expenses` (`dict[str, float]`): Pre-calculated daily expense totals.
    - `date_colors` (`list[Any]`): List of color objects (e.g. QColor) for date-based coloring.
    - `db_manager` (`DatabaseManager | None`): Database manager for currency conversion.

    Returns:

    - `list[list[Any]]`: Transformed data with colors and daily totals (display rows).

    """
    transformed_data: list[list[Any]] = []
    date_to_color_index: dict[str, int] = {}
    color_index: int = 0
    dates_with_totals: set[str] = set()

    for row in rows:
        transaction_id: int = row[0]
        amount_cents: int = row[1]
        description: str = row[2]
        category_name: str = row[3]
        currency_code: str = row[4]
        date: str = row[5]
        tag: str = row[6]
        category_type: int = row[7]
        icon: str = row[8]

        amount: float
        if db_manager:
            currency_info = db_manager.get_currency_by_code(currency_code)
            currency_id = currency_info[0] if currency_info else 1
            amount = db_manager.convert_from_minor_units(amount_cents, currency_id)
        else:
            amount = float(amount_cents) / 100

        if date not in date_to_color_index:
            date_to_color_index[date] = color_index % len(date_colors) if date_colors else 0
            color_index += 1

        color: Any = date_colors[date_to_color_index[date]] if date_colors else None

        display_category_name: str = category_name
        if icon:
            display_category_name = f"{icon} {category_name}"
        if category_type == 1:  # Income category
            display_category_name = f"{display_category_name} (Income)"

        is_first_of_day: bool = date not in dates_with_totals
        if is_first_of_day:
            dates_with_totals.add(date)

        daily_total: float = daily_expenses.get(date, 0.0)
        total_display: str = f"-{daily_total:.2f}" if is_first_of_day and daily_total > 0 else ""

        amount_display: str = f"-{amount:.2f}" if category_type == 0 else f"{amount:.2f}"

        transformed_row: list[Any] = [
            description,
            amount_display,
            display_category_name,
            currency_code,
            date,
            tag,
            total_display,
            transaction_id,
            color,
        ]
        transformed_data.append(transformed_row)

    return transformed_data
