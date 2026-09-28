"""Local daily expense totals for `tableView_transactions` without reloading the table."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from harrix_swiss_knife.apps.finance.number_utils import clean_number_text, format_amount
from harrix_swiss_knife.apps.finance.transaction_helpers import convert_currency_amount

if TYPE_CHECKING:
    from PySide6.QtWidgets import QTableView

TRANSACTION_COL_AMOUNT = 2
TRANSACTION_COL_CATEGORY = 3
TRANSACTION_COL_CURRENCY = 4
TRANSACTION_COL_DATE = 5
TRANSACTION_COL_TOTAL_PER_DAY = 7
_INCOME_MARKER = "(Income)"
_TOTAL_ALIGN_TOP = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
_TOTAL_ALIGN_MIDDLE = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


def apply_transaction_day_spans(view: QTableView) -> None:
    """Merge the Total per day column so each calendar day is one cell.

    The day's total stays right-aligned and sits at the top of the merged cell.

    """
    model = view.model()
    view.clearSpans()
    if model is None:
        return
    dates = [str(model.index(row, TRANSACTION_COL_DATE).data() or "") for row in range(model.rowCount())]
    spans = transaction_day_row_spans(dates)
    span_starts = {start for start, _row_count in spans}
    source = _transaction_source_model(model)
    if source is not None:
        source.blockSignals(True)  # noqa: FBT003
    try:
        for row in range(model.rowCount()):
            item = _transaction_total_item(model, row)
            if item is None:
                continue
            alignment = _TOTAL_ALIGN_TOP if row in span_starts else _TOTAL_ALIGN_MIDDLE
            if item.textAlignment() != alignment:
                item.setTextAlignment(alignment)
        for start, row_count in spans:
            view.setSpan(start, TRANSACTION_COL_TOTAL_PER_DAY, row_count, 1)
    finally:
        if source is not None:
            source.blockSignals(False)  # noqa: FBT003


def expense_in_default_currency(
    amount_major: float,
    *,
    is_income: bool,
    currency_code: str,
    date: str,
    db_manager: Any | None,
) -> float:
    """Return an expense in the default currency, or `0` for income.

    Args:

    - `amount_major` (`float`): Absolute amount in the transaction currency.
    - `is_income` (`bool`): Whether the row is income.
    - `currency_code` (`str`): Transaction currency code.
    - `date` (`str`): Transaction date `YYYY-MM-DD`.
    - `db_manager` (`Any | None`): Database manager for FX conversion.

    Returns:

    - `float`: Expense in the default currency.

    """
    if is_income or amount_major <= 0:
        return 0.0
    if db_manager is None:
        return amount_major
    currency_info = db_manager.get_currency_by_code(currency_code)
    source_id = currency_info[0] if currency_info else 1
    target_id = db_manager.get_default_currency_id()
    return convert_currency_amount(amount_major, source_id, target_id, db_manager, date)


def format_transaction_day_total(total: float) -> str:
    """Format the last-column daily expense the same way as table load.

    Args:

    - `total` (`float`): Daily expense in the default currency.

    Returns:

    - `str`: `-{total:.2f}` when `total > 0`, otherwise empty.

    """
    return f"-{total:.2f}" if total > 0 else ""


def format_transaction_selection_status(count: int, total: float, currency_symbol: str) -> str:
    """Format the status-bar text for selected transaction rows.

    Args:

    - `count` (`int`): Number of selected rows.
    - `total` (`float`): Signed sum in the default currency (income +, expense -).
    - `currency_symbol` (`str`): Default currency symbol.

    Returns:

    - `str`: Status text, or empty when nothing is selected.

    """
    if count <= 0:
        return ""
    rows_word = "row" if count == 1 else "rows"
    formatted = format_amount(f"{total:.2f}")
    return f"{count} {rows_word} selected · sum {formatted}{currency_symbol}"


def is_income_category_display(category: str) -> bool:
    """Return whether a category cell is shown as income."""
    return _INCOME_MARKER in category


def parse_transaction_amount_display(text: str) -> float:
    """Parse a stored amount cell, ignoring the expense minus sign.

    Args:

    - `text` (`str`): Amount text from the table model.

    Returns:

    - `float`: Absolute major-unit amount.

    """
    cleaned = clean_number_text(str(text or ""))
    if not cleaned or cleaned in {"-", ".", "-."}:
        return 0.0
    try:
        return abs(float(cleaned))
    except ValueError:
        return 0.0


def refresh_transaction_day_totals(model: QStandardItemModel, db_manager: Any | None) -> dict[str, float]:
    """Recalculate the Total per day column from the open transactions model.

    Does not emit `dataChanged` (signals are blocked) so auto-save does not run
    again.

    Args:

    - `model` (`QStandardItemModel`): Transactions source model.
    - `db_manager` (`Any | None`): Database manager for FX conversion.

    Returns:

    - `dict[str, float]`: Date → daily expense in the default currency.

    """
    row_count = model.rowCount()
    dates: list[str] = []
    totals: dict[str, float] = {}

    for row in range(row_count):
        date_str = _item_text(model, row, TRANSACTION_COL_DATE)
        amount = parse_transaction_amount_display(_item_text(model, row, TRANSACTION_COL_AMOUNT))
        expense = expense_in_default_currency(
            amount,
            is_income=is_income_category_display(_item_text(model, row, TRANSACTION_COL_CATEGORY)),
            currency_code=_item_text(model, row, TRANSACTION_COL_CURRENCY),
            date=date_str,
            db_manager=db_manager,
        )
        dates.append(date_str)
        if date_str:
            totals[date_str] = totals.get(date_str, 0.0) + expense

    seen_dates: set[str] = set()
    model.blockSignals(True)  # noqa: FBT003
    try:
        for row in range(row_count):
            date_str = dates[row]
            is_first = bool(date_str) and date_str not in seen_dates
            if is_first:
                seen_dates.add(date_str)
            total_text = format_transaction_day_total(totals.get(date_str, 0.0)) if is_first else ""
            _set_item_text(model, row, TRANSACTION_COL_TOTAL_PER_DAY, total_text)
    finally:
        model.blockSignals(False)  # noqa: FBT003

    return totals


def signed_amount_in_default_currency(
    amount_major: float,
    *,
    is_income: bool,
    currency_code: str,
    date: str,
    db_manager: Any | None,
) -> float:
    """Return a signed amount in the default currency (income +, expense -).

    Args:

    - `amount_major` (`float`): Absolute amount in the transaction currency.
    - `is_income` (`bool`): Whether the row is income.
    - `currency_code` (`str`): Transaction currency code.
    - `date` (`str`): Transaction date `YYYY-MM-DD`.
    - `db_manager` (`Any | None`): Database manager for FX conversion.

    Returns:

    - `float`: Signed amount in the default currency.

    """
    if amount_major <= 0:
        return 0.0
    if db_manager is None:
        converted = amount_major
    else:
        currency_info = db_manager.get_currency_by_code(currency_code)
        source_id = currency_info[0] if currency_info else 1
        target_id = db_manager.get_default_currency_id()
        converted = convert_currency_amount(amount_major, source_id, target_id, db_manager, date)
    return converted if is_income else -converted


def sum_transaction_rows_in_default_currency(
    model: QStandardItemModel,
    source_rows: list[int],
    db_manager: Any | None,
) -> tuple[int, float]:
    """Sum selected transaction rows in the default currency.

    Args:

    - `model` (`QStandardItemModel`): Transactions source model.
    - `source_rows` (`list[int]`): Source-model row indexes.
    - `db_manager` (`Any | None`): Database manager for FX conversion.

    Returns:

    - `tuple[int, float]`: Selected row count and signed sum.

    """
    total = 0.0
    count = 0
    row_count = model.rowCount()
    for row in source_rows:
        if row < 0 or row >= row_count:
            continue
        amount = parse_transaction_amount_display(_item_text(model, row, TRANSACTION_COL_AMOUNT))
        total += signed_amount_in_default_currency(
            amount,
            is_income=is_income_category_display(_item_text(model, row, TRANSACTION_COL_CATEGORY)),
            currency_code=_item_text(model, row, TRANSACTION_COL_CURRENCY),
            date=_item_text(model, row, TRANSACTION_COL_DATE),
            db_manager=db_manager,
        )
        count += 1
    return count, total


def transaction_day_row_spans(dates: list[str]) -> list[tuple[int, int]]:
    """Return `(start_row, row_count)` for days that occupy more than one row."""
    spans: list[tuple[int, int]] = []
    start = 0
    row_count = len(dates)
    while start < row_count:
        day = dates[start]
        end = start + 1
        while end < row_count and day and dates[end] == day:
            end += 1
        if day and end - start > 1:
            spans.append((start, end - start))
        start = end
    return spans


def _item_text(model: QStandardItemModel, row: int, column: int) -> str:
    item = model.item(row, column)
    return item.text() if item is not None else ""


def _set_item_text(model: QStandardItemModel, row: int, column: int, text: str) -> None:
    item = model.item(row, column)
    if item is not None:
        item.setText(text)


def _transaction_source_model(model: object) -> QStandardItemModel | None:
    source_fn = getattr(model, "sourceModel", None)
    if callable(source_fn):
        source = source_fn()
        if isinstance(source, QStandardItemModel):
            return source
    if isinstance(model, QStandardItemModel):
        return model
    return None


def _transaction_total_item(model: object, row: int) -> QStandardItem | None:
    index_fn = getattr(model, "index", None)
    if not callable(index_fn):
        return None
    index = index_fn(row, TRANSACTION_COL_TOTAL_PER_DAY)
    item_model = model
    item_row = row
    map_fn = getattr(model, "mapToSource", None)
    source_fn = getattr(model, "sourceModel", None)
    if callable(map_fn) and callable(source_fn):
        mapped = map_fn(index)
        source = source_fn()
        if isinstance(source, QStandardItemModel) and mapped.isValid():
            item_model = source
            item_row = mapped.row()
    if not isinstance(item_model, QStandardItemModel):
        return None
    return item_model.item(item_row, TRANSACTION_COL_TOTAL_PER_DAY)
