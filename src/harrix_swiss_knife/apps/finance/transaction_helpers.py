"""Pure calculation and transformation helpers for finance transaction data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager

# Minimum row length for get_filtered_transactions / get_all_transactions (up to category_type index 7)
MIN_TRANSACTION_ROW_LENGTH = 8

# Minimum row length for get_all_currency_exchanges (up to date index 7, description 8)
MIN_EXCHANGE_ROW_LENGTH = 9


def get_daily_total_in_currency(
    rows: list[list[Any]],
    date: str,
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
    expenses_only: bool = True,
) -> float:
    """Sum transactions for one date, each converted to target currency then summed.

    Each transaction amount is converted via money_amount_in_currency to the target
    currency (at that transaction's date), then all are summed. So multi-currency
    purchases are converted first, then summed — not summed then converted.

    Args:

    - `rows` (`list[list[Any]]`): Raw transaction data (same format as get_filtered_transactions).
    - `date` (`str`): Date to sum (YYYY-MM-DD).
    - `db_manager` (`DatabaseManager | None`): Database manager for conversion.
    - `target_currency_id` (`int | None`): Target currency ID. None = project default currency.
    - `expenses_only` (`bool`): If True, sum only expenses (category_type==0). If False, sum all
      (expenses negative, income positive). Default True for "Total per day" style.

    Returns:

    - `float`: Sum for that date in target currency (major units). Always non-negative when
      expenses_only=True.

    """
    total: float = 0.0
    for row in rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        row_date: str = row[5]
        if row_date != date:
            continue
        amount_cents: int = row[1]
        category_type: int = row[7]
        if expenses_only and category_type != 0:
            continue
        if db_manager is None:
            total += float(amount_cents) / 100
            continue
        currency_code: str = row[4]
        currency_info = db_manager.get_currency_by_code(currency_code)
        source_currency_id: int = currency_info[0] if currency_info else 1
        converted: float = money_amount_in_currency(
            amount_cents, source_currency_id, db_manager, target_currency_id=target_currency_id, date=row_date
        )
        if expenses_only:
            total += converted
        else:
            sign: int = -1 if category_type == 0 else 1
            total += sign * converted
    return total


def calculate_daily_expenses(
    rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> dict[str, float]:
    """Calculate daily expenses from transaction data in target or default currency.

    Each expense is converted to target currency at the transaction date via
    money_amount_in_currency, then summed per day. So each amount is converted
    first, then summed — not summed then converted.

    Args:

    - `rows` (`list[list[Any]]`): Raw transaction data from database.
    - `db_manager` (`DatabaseManager | None`): Database manager for currency conversion.
    - `target_currency_id` (`int | None`): Target currency ID. None = project default currency.

    Returns:

    - `dict[str, float]`: Dictionary mapping dates to total expenses for that day (in target currency).

    """
    daily_expenses: dict[str, float] = {}

    for row in rows:
        amount_cents: int = row[1]
        date: str = row[5]
        category_type: int = row[7]

        # Only count expenses (category_type == 0)
        if category_type == 0:
            if db_manager:
                currency_code: str = row[4]
                currency_info = db_manager.get_currency_by_code(currency_code)
                source_currency_id: int = currency_info[0] if currency_info else 1
                amount = money_amount_in_currency(
                    amount_cents,
                    source_currency_id,
                    db_manager,
                    target_currency_id=target_currency_id,
                    date=date,
                )
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


def currency_exchange_expense_values(
    row: list[Any],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> tuple[float, float]:
    """Return fee and loss expense values for one currency exchange row in target currency.

    Both returned values are non-negative (expense amounts). Uses exchange rate at
    the exchange date. If target_currency_id is None, uses default currency from settings.

    Row format: same as get_all_currency_exchanges():
    [ce._id, from_code, to_code, amount_from, amount_to, exchange_rate, fee, date, description].
    amount_from, amount_to, fee are in minor units.

    Args:

    - `row` (`list[Any]`): One currency exchange row (at least 9 elements).
    - `db_manager` (`DatabaseManager | None`): Database manager for rates and default currency.
    - `target_currency_id` (`int | None`): Target currency ID. None = default currency.

    Returns:

    - `tuple[float, float]`: (fee_in_target_currency, loss_in_target_currency) in major units.

    """
    if db_manager is None or len(row) < MIN_EXCHANGE_ROW_LENGTH:
        return (0.0, 0.0)
    try:
        from_code: str = row[1]
        to_code: str = row[2]
        exchange_date: str = row[7]

        from_currency_info = db_manager.get_currency_by_code(from_code)
        to_currency_info = db_manager.get_currency_by_code(to_code)
        if not from_currency_info or not to_currency_info:
            return (0.0, 0.0)

        from_currency_id: int = from_currency_info[0]
        to_currency_id: int = to_currency_info[0]

        amount_from_major: float = db_manager.convert_from_minor_units(row[3], from_currency_id)
        amount_to_major: float = db_manager.convert_from_minor_units(row[4], to_currency_id)
        fee_major: float = db_manager.convert_from_minor_units(row[6] or 0, from_currency_id)

        if target_currency_id is None:
            target_currency_id = db_manager.get_default_currency_id()

        fee_in_target: float = convert_currency_amount(
            fee_major, from_currency_id, target_currency_id, db_manager, exchange_date
        )
        fee_in_target = abs(fee_in_target)

        default_currency_id: int = db_manager.get_default_currency_id()
        loss_in_default: float = calculate_exchange_loss(
            from_currency_id,
            to_currency_id,
            amount_from_major,
            amount_to_major,
            default_currency_id,
            db_manager,
            fee=fee_major,
            use_date=exchange_date,
        )
        if target_currency_id == default_currency_id:
            loss_in_target: float = abs(loss_in_default)
        else:
            loss_in_target = abs(
                convert_currency_amount(
                    loss_in_default,
                    default_currency_id,
                    target_currency_id,
                    db_manager,
                    exchange_date,
                )
            )

        return (fee_in_target, loss_in_target)
    except Exception as e:
        print(f"Error computing currency exchange expense values: {e}")
        return (0.0, 0.0)


def currency_exchange_fee_and_loss_signed(
    row: list[Any],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> tuple[float, float]:
    """Return fee and loss/profit for one currency exchange row in target currency (signed).

    Fee: positive = we pay (expense), negative = refund. Loss: negative = loss (expense),
    positive = profit (income). Uses exchange rate at the exchange date.

    Row format: same as get_all_currency_exchanges():
    [ce._id, from_code, to_code, amount_from, amount_to, exchange_rate, fee, date, description].

    Args:

    - `row` (`list[Any]`): One currency exchange row (at least 9 elements).
    - `db_manager` (`DatabaseManager | None`): Database manager for rates and default currency.
    - `target_currency_id` (`int | None`): Target currency ID. None = default currency.

    Returns:

    - `tuple[float, float]`: (fee_signed, loss_signed) in target currency (major units).
      fee_signed: positive = expense, negative = refund. loss_signed: negative = loss, positive = profit.

    """
    if db_manager is None or len(row) < MIN_EXCHANGE_ROW_LENGTH:
        return (0.0, 0.0)
    try:
        from_code: str = row[1]
        to_code: str = row[2]
        exchange_date: str = row[7]

        from_currency_info = db_manager.get_currency_by_code(from_code)
        to_currency_info = db_manager.get_currency_by_code(to_code)
        if not from_currency_info or not to_currency_info:
            return (0.0, 0.0)

        from_currency_id: int = from_currency_info[0]
        to_currency_id: int = to_currency_info[0]

        amount_from_major: float = db_manager.convert_from_minor_units(row[3], from_currency_id)
        amount_to_major: float = db_manager.convert_from_minor_units(row[4], to_currency_id)
        fee_major: float = db_manager.convert_from_minor_units(row[6] or 0, from_currency_id)

        if target_currency_id is None:
            target_currency_id = db_manager.get_default_currency_id()

        fee_in_target: float = convert_currency_amount(
            fee_major, from_currency_id, target_currency_id, db_manager, exchange_date
        )

        default_currency_id: int = db_manager.get_default_currency_id()
        loss_in_default: float = calculate_exchange_loss(
            from_currency_id,
            to_currency_id,
            amount_from_major,
            amount_to_major,
            default_currency_id,
            db_manager,
            fee=fee_major,
            use_date=exchange_date,
        )
        if target_currency_id == default_currency_id:
            loss_in_target_signed: float = loss_in_default
        else:
            loss_abs: float = abs(loss_in_default)
            loss_in_target: float = convert_currency_amount(
                loss_abs,
                default_currency_id,
                target_currency_id,
                db_manager,
                exchange_date,
            )
            loss_in_target_signed = loss_in_target if loss_in_default >= 0 else -loss_in_target

        return (fee_in_target, loss_in_target_signed)
    except Exception as e:
        print(f"Error computing currency exchange fee and loss (signed): {e}")
        return (0.0, 0.0)


def get_daily_expenses_total(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    date: str,
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> float:
    """Total expenses for one date in target currency (transactions + exchange fee and loss).

    Uses get_daily_total_in_currency for transaction expenses. Adds exchange-related
    expenses for that date: fee (positive = we pay; negative fee reduces expenses) and
    loss from currency exchange (when loss is negative, its absolute value is added).
    Each amount is converted to target currency before summing.

    Args:

    - `transaction_rows` (`list[list[Any]]`): Raw transaction data (e.g. get_filtered_transactions).
    - `exchange_rows` (`list[list[Any]]`): All currency exchange rows (e.g. get_all_currency_exchanges).
    - `date` (`str`): Date (YYYY-MM-DD).
    - `db_manager` (`DatabaseManager | None`): Database manager.
    - `target_currency_id` (`int | None`): Target currency. None = project default.

    Returns:

    - `float`: Total expenses for the date in target currency (non-negative).

    """
    total: float = get_daily_total_in_currency(
        transaction_rows,
        date,
        db_manager,
        target_currency_id=target_currency_id,
        expenses_only=True,
    )
    for row in exchange_rows:
        if len(row) < MIN_EXCHANGE_ROW_LENGTH or row[7] != date:
            continue
        fee_signed: float
        loss_signed: float
        fee_signed, loss_signed = currency_exchange_fee_and_loss_signed(
            row, db_manager, target_currency_id=target_currency_id
        )
        if fee_signed > 0:
            total += fee_signed
        elif fee_signed < 0:
            total -= abs(fee_signed)
        if loss_signed < 0:
            total += abs(loss_signed)
    return max(0.0, total)


def get_daily_income_total(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    date: str,
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> float:
    """Total income for one date in target currency (income transactions + exchange profit).

    Sums income transactions (category_type==1) converted to target currency, plus
    profit from currency exchanges on that date (when exchange loss calculation
    returns positive = profit). Each amount is converted to target currency.

    Args:

    - `transaction_rows` (`list[list[Any]]`): Raw transaction data.
    - `exchange_rows` (`list[list[Any]]`): All currency exchange rows.
    - `date` (`str`): Date (YYYY-MM-DD).
    - `db_manager` (`DatabaseManager | None`): Database manager.
    - `target_currency_id` (`int | None`): Target currency. None = project default.

    Returns:

    - `float`: Total income for the date in target currency (non-negative).

    """
    income_total: float = 0.0
    for row in transaction_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH or row[5] != date or row[7] != 1:
            continue
        amount_cents: int = row[1]
        if db_manager is None:
            income_total += float(amount_cents) / 100
            continue
        currency_code: str = row[4]
        currency_info = db_manager.get_currency_by_code(currency_code)
        source_currency_id: int = currency_info[0] if currency_info else 1
        income_total += money_amount_in_currency(
            amount_cents,
            source_currency_id,
            db_manager,
            target_currency_id=target_currency_id,
            date=row[5],
        )
    for ex_row in exchange_rows:
        if len(ex_row) < MIN_EXCHANGE_ROW_LENGTH or ex_row[7] != date:
            continue
        _fee_signed, loss_signed = currency_exchange_fee_and_loss_signed(
            ex_row, db_manager, target_currency_id=target_currency_id
        )
        if loss_signed > 0:
            income_total += loss_signed
    return max(0.0, income_total)


def get_daily_expenses_and_income_totals(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> tuple[dict[str, float], dict[str, float]]:
    """Build dictionaries of daily expenses and income in target currency (one pass, no per-date DB).

    Expenses per day: transaction expenses (category_type==0) plus exchange fee (when > 0)
    and exchange loss (when loss < 0). Income per day: income transactions (category_type==1)
    plus exchange profit (when loss > 0). All amounts converted to target currency.
    Uses only the provided lists; no extra database queries per date. Suitable for charts.

    Args:

    - `transaction_rows` (`list[list[Any]]`): Raw transaction data (e.g. get_filtered_transactions).
    - `exchange_rows` (`list[list[Any]]`): All currency exchange rows (e.g. get_all_currency_exchanges).
    - `db_manager` (`DatabaseManager | None`): Database manager for conversion.
    - `target_currency_id` (`int | None`): Target currency. None = project default.

    Returns:

    - `tuple[dict[str, float], dict[str, float]]`: (expenses_by_date, income_by_date).
      Keys are date strings YYYY-MM-DD. Values are non-negative sums in target currency.

    """
    expenses_by_date: dict[str, float] = {}
    income_by_date: dict[str, float] = {}

    for row in transaction_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        date_str: str = row[5]
        amount_cents: int = row[1]
        category_type: int = row[7]
        if db_manager is None:
            amount = float(amount_cents) / 100
        else:
            currency_code: str = row[4]
            currency_info = db_manager.get_currency_by_code(currency_code)
            source_currency_id: int = currency_info[0] if currency_info else 1
            amount = money_amount_in_currency(
                amount_cents,
                source_currency_id,
                db_manager,
                target_currency_id=target_currency_id,
                date=date_str,
            )
        if category_type == 0:
            expenses_by_date[date_str] = expenses_by_date.get(date_str, 0.0) + amount
        else:
            income_by_date[date_str] = income_by_date.get(date_str, 0.0) + amount

    for row in exchange_rows:
        if len(row) < MIN_EXCHANGE_ROW_LENGTH:
            continue
        date_str = row[7]
        fee_signed: float
        loss_signed: float
        fee_signed, loss_signed = currency_exchange_fee_and_loss_signed(
            row, db_manager, target_currency_id=target_currency_id
        )
        if fee_signed != 0:
            expenses_by_date[date_str] = expenses_by_date.get(date_str, 0.0) + fee_signed
        if loss_signed < 0:
            expenses_by_date[date_str] = expenses_by_date.get(date_str, 0.0) + abs(loss_signed)
        elif loss_signed > 0:
            income_by_date[date_str] = income_by_date.get(date_str, 0.0) + loss_signed

    for key in expenses_by_date:
        expenses_by_date[key] = max(0.0, expenses_by_date[key])
    for key in income_by_date:
        income_by_date[key] = max(0.0, income_by_date[key])

    return expenses_by_date, income_by_date


def money_amount_in_currency(
    amount_minor: int,
    source_currency_id: int,
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
    date: str | None = None,
) -> float:
    """Convert arbitrary amount from source currency to target currency.

    Input amount is in minor units (e.g. kopecks, cents), as stored in transactions.
    Result is in major units (e.g. rubles, euros) in target currency. Uses exchange
    rate for the given date; if date is None, uses today. If target_currency_id is
    None, uses project default currency.

    Args:

    - `amount_minor` (`int`): Amount in minor units (same as in transactions).
    - `source_currency_id` (`int`): Source currency ID.
    - `db_manager` (`DatabaseManager | None`): Database manager for rates and default currency.
    - `target_currency_id` (`int | None`): Target currency ID. None = default currency.
    - `date` (`str | None`): Date for exchange rate (YYYY-MM-DD). None = today.

    Returns:

    - `float`: Amount in target currency in major units.

    """
    if db_manager is None:
        return 0.0
    try:
        amount_major: float = db_manager.convert_from_minor_units(amount_minor, source_currency_id)
        if target_currency_id is None:
            target_currency_id = db_manager.get_default_currency_id()
        return convert_currency_amount(amount_major, source_currency_id, target_currency_id, db_manager, date)
    except Exception as e:
        print(f"Error converting money amount to currency: {e}")
        return 0.0


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
