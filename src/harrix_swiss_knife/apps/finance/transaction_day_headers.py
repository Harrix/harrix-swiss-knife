"""Day and month group headers for the Finance Transactions table.

Inserts display-only header rows above each consecutive date run in the current
view order (after sorting/filtering), plus month summary banners:

- at the top: current calendar month income/expenses from the open view;
- above the newest day of each earlier month (the calendar last date when the
  table is sorted newest-first).

Headers are not transactions: they are not selectable as data rows and are
skipped by calculation helpers that walk the ultimate `QStandardItemModel`.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, overload

from PySide6.QtCore import (
    QAbstractItemModel,
    QAbstractProxyModel,
    QDate,
    QLocale,
    QModelIndex,
    QObject,
    QRect,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QAbstractItemDelegate, QStyledItemDelegate, QStyleOptionViewItem, QTableView, QWidget

from harrix_swiss_knife.apps.common.day_bands import DAY_BAND_ROLE, day_band_color
from harrix_swiss_knife.apps.common.ui_chrome import HAIRLINE
from harrix_swiss_knife.apps.finance.number_utils import format_amount, with_currency
from harrix_swiss_knife.apps.finance.transaction_day_totals import (
    TRANSACTION_COL_AMOUNT,
    TRANSACTION_COL_CATEGORY,
    TRANSACTION_COL_DATE,
    TRANSACTION_COL_TOTAL_PER_DAY,
    is_income_category_display,
    parse_transaction_amount_display,
)
from harrix_swiss_knife.apps.finance.transactions_ui_settings import TRANSACTION_COL_TAG
from harrix_swiss_knife.fluent.theme import FluentTheme, mix, palette_for

if TYPE_CHECKING:
    from PySide6.QtCore import QPersistentModelIndex

IS_DAY_HEADER_ROLE = Qt.ItemDataRole.UserRole + 520
DAY_HEADER_DATE_ROLE = Qt.ItemDataRole.UserRole + 521
DAY_HEADER_TOTAL_ROLE = Qt.ItemDataRole.UserRole + 522
DAY_HEADER_INCOME_ROLE = Qt.ItemDataRole.UserRole + 523
IS_MONTH_HEADER_ROLE = Qt.ItemDataRole.UserRole + 524
DAY_HEADER_IS_CURRENT_MONTH_ROLE = Qt.ItemDataRole.UserRole + 525

_HEADER_PAD_X = 8
_HEADER_TOTAL_GAP = 12
_SEPARATOR_ALPHA = 90
_MONTH_SEPARATOR_ALPHA = 160
_MONTH_MIN_HEIGHT = 36
_MONTH_WASH_ALPHA_DARK = 28
_PROXY_DAY_HEADER = -1
_PROXY_MONTH_HEADER = -2
_YYYY_MM_PARTS = 2
_MONTHS_IN_YEAR = 12
_YYYY_MM_PREFIX_LEN = 7
# Theme day-band refresh paints fills only — must not rebuild headers per cell.
_COSMETIC_ROLES = frozenset(
    {
        int(Qt.ItemDataRole.BackgroundRole),
        int(Qt.ItemDataRole.ForegroundRole),
        int(Qt.ItemDataRole.FontRole),
        int(Qt.ItemDataRole.DecorationRole),
        int(DAY_BAND_ROLE),
    },
)


class DayHeaderDelegate(QStyledItemDelegate):
    """Paint day/month headers (date left, totals above Amount) for spanned rows."""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the day/month header chrome, or fall through for ordinary cells."""
        is_day = bool(index.data(IS_DAY_HEADER_ROLE))
        is_month = bool(index.data(IS_MONTH_HEADER_ROLE))
        if not is_day and not is_month:
            super().paint(painter, option, index)
            return

        date_text = str(index.data(DAY_HEADER_DATE_ROLE) or "")
        total_raw = str(index.data(DAY_HEADER_TOTAL_ROLE) or "")
        income_raw = str(index.data(DAY_HEADER_INCOME_ROLE) or "")
        host = option.widget if isinstance(option.widget, QWidget) else None
        fluent = palette_for(host)
        fill = index.data(Qt.ItemDataRole.BackgroundRole)
        # Month banners always follow the painting host — model BackgroundRole
        # used to call palette_for(None) and stayed light under Fluent dark.
        if is_month:
            background = _month_header_fill(fluent)
        elif isinstance(fill, QColor):
            background = fill
        else:
            background = mix(fluent.window_bg, fluent.card_bg)
        ink = mix(fluent.window_bg, fluent.text_primary)
        muted = mix(fluent.window_bg, fluent.text_secondary)
        hairline = mix(fluent.window_bg, fluent.divider)
        hairline.setAlpha(_MONTH_SEPARATOR_ALPHA if is_month else _SEPARATOR_ALPHA)

        painter.save()
        painter.fillRect(option.rect, background)
        # Month: stronger top rule (no accent bar — that reads as selection chrome).
        if is_month or index.row() > 0:
            painter.setPen(QPen(hairline, 1))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())

        date_font = QFont(option.font)
        date_font.setBold(True)
        total_font = QFont(option.font)
        total_font.setBold(True)
        if total_font.pointSize() > 0:
            total_font.setPointSize(total_font.pointSize() + (2 if is_month else 1))
        date_metrics = QFontMetrics(date_font)
        total_metrics = QFontMetrics(total_font)
        # Align day totals with the Amount column so they do not sit over Tag.
        total_right = _day_header_total_right(host, option.rect)
        text_left = option.rect.left() + _HEADER_PAD_X
        text_right = max(text_left, total_right - _HEADER_PAD_X)
        text_rect = QRect(text_left, option.rect.top(), text_right - text_left, option.rect.height())

        income_display = _format_header_income(income_raw, host)
        # Month banners always spell out Expenses when both sides exist.
        expense_display = _format_header_total(
            total_raw,
            host,
            has_income=bool(income_display) or is_month,
        )
        expense_width = total_metrics.horizontalAdvance(expense_display) if expense_display else 0
        income_width = total_metrics.horizontalAdvance(income_display) if income_display else 0
        totals_gap = _HEADER_TOTAL_GAP if expense_display and income_display else 0
        totals_width = expense_width + income_width + totals_gap
        date_width = max(0, text_rect.width() - totals_width - 12)
        painter.setFont(date_font)
        painter.setPen(ink if is_month else muted)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            date_metrics.elidedText(date_text, Qt.TextElideMode.ElideRight, date_width),
        )
        cursor_right = text_rect.right()
        painter.setFont(total_font)
        if expense_display:
            painter.setPen(ink if "-" in expense_display or is_month else fluent.success)
            expense_rect = QRect(
                cursor_right - expense_width,
                text_rect.top(),
                expense_width,
                text_rect.height(),
            )
            painter.drawText(
                expense_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                expense_display,
            )
            cursor_right = expense_rect.left() - totals_gap
        if income_display:
            painter.setPen(fluent.success)
            income_rect = QRect(
                cursor_right - income_width,
                text_rect.top(),
                income_width,
                text_rect.height(),
            )
            painter.drawText(
                income_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                income_display,
            )
        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Make month banners slightly taller than day headers."""
        hint = super().sizeHint(option, index)
        if bool(index.data(IS_MONTH_HEADER_ROLE)):
            return QSize(hint.width(), max(hint.height(), _MONTH_MIN_HEIGHT))
        return hint


class TransactionDayHeaderProxy(QAbstractProxyModel):
    """Proxy that inserts day and month header rows into the transaction list."""

    mapping_reset = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        """Create an empty day-header proxy."""
        super().__init__(parent)
        self._proxy_rows: list[int] = []  # source row, or negative sentinel for a header
        self._header_dates: dict[int, str] = {}
        self._header_totals: dict[int, str] = {}
        self._header_incomes: dict[int, str] = {}
        self._header_bands: dict[int, int] = {}
        self._header_month_rows: set[int] = set()
        self._header_current_month_rows: set[int] = set()
        self._source_to_proxy: dict[int, int] = {}
        self._rebuild_scheduled = False
        # Tests can pin the “current” month without freezing the clock.
        self.current_month_key_override: str | None = None

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:  # noqa: N802
        """Match the source column count."""
        if parent is not None and parent.isValid():
            return 0
        source = self.sourceModel()
        return 0 if source is None else source.columnCount()

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return header metadata or forward to the source model."""
        if not index.isValid():
            return None
        proxy_row = index.row()
        if self._is_header_row(proxy_row):
            is_month = proxy_row in self._header_month_rows
            if role == IS_DAY_HEADER_ROLE:
                return not is_month
            if role == IS_MONTH_HEADER_ROLE:
                return is_month
            if role == DAY_HEADER_IS_CURRENT_MONTH_ROLE:
                return proxy_row in self._header_current_month_rows
            if role == DAY_HEADER_DATE_ROLE:
                return self._header_dates.get(proxy_row, "")
            if role == DAY_HEADER_TOTAL_ROLE:
                return self._header_totals.get(proxy_row, "")
            if role == DAY_HEADER_INCOME_ROLE:
                return self._header_incomes.get(proxy_row, "")
            if role == Qt.ItemDataRole.DisplayRole:
                if index.column() == 0:
                    return self._header_dates.get(proxy_row, "")
                if index.column() == TRANSACTION_COL_TOTAL_PER_DAY:
                    return self._header_totals.get(proxy_row, "")
                return ""
            if role == Qt.ItemDataRole.BackgroundRole:
                if is_month:
                    return _month_header_fill(FluentTheme.instance().palette())
                return day_band_color(self._band_index_for_header(proxy_row))
            if role in {Qt.ItemDataRole.FontRole, Qt.ItemDataRole.TextAlignmentRole}:
                return None
            return None
        source_index = self.mapToSource(index)
        if not source_index.isValid():
            return None
        source = self.sourceModel()
        return None if source is None else source.data(source_index, role)

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        """Headers are enabled only (not selectable or editable)."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if self._is_header_row(index.row()):
            return Qt.ItemFlag.ItemIsEnabled
        source_index = self.mapToSource(index)
        source = self.sourceModel()
        if source is None or not source_index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return source.flags(source_index)

    def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Forward horizontal headers; leave vertical IDs empty on day/month headers."""
        source = self.sourceModel()
        if source is None:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return source.headerData(section, orientation, role)
        if section < 0 or section >= len(self._proxy_rows):
            return None
        if self._is_header_row(section):
            if role == Qt.ItemDataRole.DisplayRole:
                return ""
            if role == Qt.ItemDataRole.BackgroundRole:
                if section in self._header_month_rows:
                    return _month_header_fill(FluentTheme.instance().palette())
                return day_band_color(self._band_index_for_header(section))
            return None
        source_row = self._proxy_rows[section]
        return source.headerData(source_row, orientation, role)

    def index(
        self,
        row: int,
        column: int,
        parent: QModelIndex | QPersistentModelIndex | None = None,
    ) -> QModelIndex:
        """Create a proxy index for a mapped row."""
        if parent is not None and parent.isValid():
            return QModelIndex()
        if row < 0 or column < 0 or row >= len(self._proxy_rows) or column >= self.columnCount():
            return QModelIndex()
        return self.createIndex(row, column)

    def mapFromSource(self, source_index: QModelIndex | QPersistentModelIndex) -> QModelIndex:  # noqa: N802
        """Map a source index to the corresponding proxy data row."""
        if not source_index.isValid():
            return QModelIndex()
        proxy_row = self._source_to_proxy.get(source_index.row())
        if proxy_row is None:
            return QModelIndex()
        return self.index(proxy_row, source_index.column())

    def mapToSource(self, proxy_index: QModelIndex | QPersistentModelIndex) -> QModelIndex:  # noqa: N802
        """Map a proxy data row to the source; headers map to an invalid index."""
        if not proxy_index.isValid() or self._is_header_row(proxy_index.row()):
            return QModelIndex()
        source = self.sourceModel()
        if source is None:
            return QModelIndex()
        source_row = self._proxy_rows[proxy_index.row()]
        return source.index(source_row, proxy_index.column())

    @overload
    def parent(self, /) -> QObject | None: ...

    @overload
    def parent(self, child: QModelIndex | QPersistentModelIndex, /) -> QModelIndex: ...

    def parent(
        self,
        child: QModelIndex | QPersistentModelIndex | None = None,
        /,
    ) -> QModelIndex | QObject | None:
        """QObject parent, or an invalid model parent for this flat table."""
        if child is None:
            return QObject.parent(self)
        return QModelIndex()

    def rebuild(self) -> None:
        """Rebuild header insertion from the current source row order."""
        self._rebuild_mapping()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:  # noqa: N802
        """Return data rows plus inserted day/month headers."""
        if parent is not None and parent.isValid():
            return 0
        return len(self._proxy_rows)

    def setSourceModel(self, source_model: QAbstractItemModel | None) -> None:  # noqa: N802
        """Attach `source_model` and rebuild the day-header mapping."""
        previous = self.sourceModel()
        if previous is not None:
            previous.modelReset.disconnect(self._on_source_reset)
            previous.layoutChanged.disconnect(self._on_source_reset)
            previous.rowsInserted.disconnect(self._on_source_reset)
            previous.rowsRemoved.disconnect(self._on_source_reset)
            previous.dataChanged.disconnect(self._on_source_data_changed)
        if source_model is not None:
            super().setSourceModel(source_model)
            source_model.modelReset.connect(self._on_source_reset)
            source_model.layoutChanged.connect(self._on_source_reset)
            source_model.rowsInserted.connect(self._on_source_reset)
            source_model.rowsRemoved.connect(self._on_source_reset)
            source_model.dataChanged.connect(self._on_source_data_changed)
        self._rebuild_mapping()

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """Sort the inner model, then rebuild day headers for the new order."""
        source = self.sourceModel()
        if source is None:
            return
        source.sort(column, order)
        self._rebuild_mapping()

    def _append_day_header(
        self,
        *,
        date_str: str,
        total_text: str,
        income_text: str,
        band_index: int,
    ) -> None:
        header_row = len(self._proxy_rows)
        self._proxy_rows.append(_PROXY_DAY_HEADER)
        self._header_dates[header_row] = date_str
        self._header_totals[header_row] = total_text
        self._header_incomes[header_row] = income_text
        self._header_bands[header_row] = band_index

    def _append_month_header(
        self,
        *,
        month_key: str,
        expense_text: str,
        income_text: str,
        is_current: bool,
    ) -> None:
        header_row = len(self._proxy_rows)
        self._proxy_rows.append(_PROXY_MONTH_HEADER)
        self._header_month_rows.add(header_row)
        if is_current:
            self._header_current_month_rows.add(header_row)
        self._header_dates[header_row] = _format_month_banner_label(month_key, is_current=is_current)
        self._header_totals[header_row] = expense_text
        self._header_incomes[header_row] = income_text
        self._header_bands[header_row] = 0

    def _band_index_for_header(self, proxy_row: int) -> int:
        return self._header_bands.get(proxy_row, 0)

    def _current_month_key(self) -> str:
        if self.current_month_key_override:
            return self.current_month_key_override
        return QDate.currentDate().toString("yyyy-MM")

    def _forward_source_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles: list[int] | None,
    ) -> None:
        role_args: list[int] = list(roles) if roles else []
        for source_row in range(top_left.row(), bottom_right.row() + 1):
            proxy_row = self._source_to_proxy.get(source_row)
            if proxy_row is None:
                continue
            left = self.index(proxy_row, top_left.column())
            right = self.index(proxy_row, bottom_right.column())
            if role_args:
                self.dataChanged.emit(left, right, role_args)
            else:
                self.dataChanged.emit(left, right)

    def _is_header_row(self, proxy_row: int) -> bool:
        return 0 <= proxy_row < len(self._proxy_rows) and self._proxy_rows[proxy_row] < 0

    def _on_source_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles: list[int] | None = None,
    ) -> None:
        role_values = [int(role) for role in roles] if roles else []
        # Theme refresh paints Background/Foreground on every cell, including Date
        # and Total. Rebuilding headers for each cell freezes the UI.
        if role_values and set(role_values) <= _COSMETIC_ROLES:
            self._forward_source_data_changed(top_left, bottom_right, role_values)
            return
        if (
            top_left.column() <= TRANSACTION_COL_DATE <= bottom_right.column()
            or top_left.column() <= TRANSACTION_COL_TOTAL_PER_DAY <= bottom_right.column()
            or top_left.column() <= TRANSACTION_COL_AMOUNT <= bottom_right.column()
            or top_left.column() <= TRANSACTION_COL_CATEGORY <= bottom_right.column()
        ):
            self._schedule_rebuild()
            return
        self._forward_source_data_changed(top_left, bottom_right, role_values)

    def _on_source_reset(self, *_args: object) -> None:
        self._schedule_rebuild()

    def _rebuild_mapping(self) -> None:
        self._rebuild_scheduled = False
        self.beginResetModel()
        self._proxy_rows = []
        self._header_dates = {}
        self._header_totals = {}
        self._header_incomes = {}
        self._header_bands = {}
        self._header_month_rows = set()
        self._header_current_month_rows = set()
        self._source_to_proxy = {}
        source = self.sourceModel()
        if source is None:
            self.endResetModel()
            self.mapping_reset.emit()
            return

        income_by_date = _income_totals_by_date(source)
        expense_by_month, income_by_month = _month_flow_totals(source, income_by_date)
        current_month = self._current_month_key()
        current_expense = expense_by_month.get(current_month, 0.0)
        current_income = income_by_month.get(current_month, 0.0)
        # Skip an empty current-month banner when history starts in an earlier month.
        if source.rowCount() > 0 and (current_expense > 0 or current_income > 0):
            self._append_month_header(
                month_key=current_month,
                expense_text=_expense_text_from_major(current_expense),
                income_text=_income_text_from_major(current_income),
                is_current=True,
            )

        previous_date: object = object()
        previous_month: str | None = None
        band_index = 0
        for source_row in range(source.rowCount()):
            date_value = source.index(source_row, TRANSACTION_COL_DATE).data(Qt.ItemDataRole.DisplayRole)
            date_str = "" if date_value is None else str(date_value).strip()
            month_key = _month_key(date_str)
            if date_str and date_str != previous_date:
                if month_key and month_key != previous_month:
                    # Above the newest day of this month (= calendar last day in DESC order).
                    if month_key != current_month:
                        self._append_month_header(
                            month_key=month_key,
                            expense_text=_expense_text_from_major(expense_by_month.get(month_key, 0.0)),
                            income_text=_income_text_from_major(income_by_month.get(month_key, 0.0)),
                            is_current=False,
                        )
                    previous_month = month_key
                total_value = source.index(source_row, TRANSACTION_COL_TOTAL_PER_DAY).data(Qt.ItemDataRole.DisplayRole)
                total_text = "" if total_value is None else str(total_value)
                income_major = income_by_date.get(date_str, 0.0)
                income_text = f"{income_major:.2f}" if income_major > 0 else ""
                self._append_day_header(
                    date_str=date_str,
                    total_text=total_text,
                    income_text=income_text,
                    band_index=band_index,
                )
                band_index = 1 - band_index
                previous_date = date_str
            self._source_to_proxy[source_row] = len(self._proxy_rows)
            self._proxy_rows.append(source_row)
        self.endResetModel()
        self.mapping_reset.emit()

    def _schedule_rebuild(self) -> None:
        if self._rebuild_scheduled:
            return
        self._rebuild_scheduled = True
        QTimer.singleShot(0, self._rebuild_mapping)


class _DayHeaderOrDelegate(QStyledItemDelegate):
    """Paint day/month headers; otherwise forward to the description delegate."""

    def __init__(self, inner: QAbstractItemDelegate, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._inner = inner
        self._header = DayHeaderDelegate(parent)

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        return self._inner.createEditor(parent, option, index)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if bool(index.data(IS_DAY_HEADER_ROLE)) or bool(index.data(IS_MONTH_HEADER_ROLE)):
            self._header.paint(painter, option, index)
            return
        self._inner.paint(painter, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        if bool(index.data(IS_DAY_HEADER_ROLE)) or bool(index.data(IS_MONTH_HEADER_ROLE)):
            return
        self._inner.setEditorData(editor, index)

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if bool(index.data(IS_DAY_HEADER_ROLE)) or bool(index.data(IS_MONTH_HEADER_ROLE)):
            return
        self._inner.setModelData(editor, model, index)

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        if bool(index.data(IS_DAY_HEADER_ROLE)) or bool(index.data(IS_MONTH_HEADER_ROLE)):
            return self._header.sizeHint(option, index)
        return self._inner.sizeHint(option, index)


def apply_transaction_day_header_spans(view: QTableView) -> None:
    """Span each day/month header row across all columns so one cell paints the banner."""
    model = view.model()
    view.clearSpans()
    if model is None:
        return
    columns = model.columnCount()
    if columns <= 0:
        return
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if bool(model.data(index, IS_DAY_HEADER_ROLE)) or bool(model.data(index, IS_MONTH_HEADER_ROLE)):
            view.setSpan(row, 0, 1, columns)


def install_transaction_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> TransactionDayHeaderProxy:
    """Wrap `sort_proxy` with day/month headers and show it on `view`."""
    existing = view.model()
    if isinstance(existing, TransactionDayHeaderProxy) and existing.sourceModel() is sort_proxy:
        existing.rebuild()
        apply_transaction_day_header_spans(view)
        return existing

    proxy = TransactionDayHeaderProxy(view)
    proxy.setSourceModel(sort_proxy)
    view.setModel(proxy)

    def _on_mapping_reset() -> None:
        apply_transaction_day_header_spans(view)

    proxy.mapping_reset.connect(_on_mapping_reset)
    apply_transaction_day_header_spans(view)

    description_delegate = view.itemDelegateForColumn(0)
    header_delegate = DayHeaderDelegate(view)
    if description_delegate is not None and not isinstance(description_delegate, DayHeaderDelegate):
        # Keep description editing on data rows; headers paint through this wrapper.
        header_delegate = _DayHeaderOrDelegate(description_delegate, view)
    view.setItemDelegateForColumn(0, header_delegate)
    return proxy


def map_transactions_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]:
    """Walk proxy layers until the ultimate source model index."""
    model: Any = index.model()
    current = index
    while isinstance(model, QAbstractProxyModel):
        current = model.mapToSource(current)
        if not current.isValid():
            return current, model.sourceModel()
        model = model.sourceModel()
    return current, model


def ultimate_transactions_source(model: Any) -> Any:
    """Return the innermost model under nested proxies."""
    current = model
    while isinstance(current, QAbstractProxyModel):
        current = current.sourceModel()
    return current


def _day_header_total_right(host: QWidget | None, span_rect: QRect) -> int:
    """Return the right edge for the day total (Amount column, else before Tag)."""
    if not isinstance(host, QTableView):
        return span_rect.right()
    model = host.model()
    if model is None:
        return span_rect.right()

    x = span_rect.left()
    amount_right: int | None = None
    last_non_tag_right = span_rect.left()
    for column in range(model.columnCount()):
        if host.isColumnHidden(column):
            continue
        width = host.columnWidth(column)
        right = x + width
        if column == TRANSACTION_COL_AMOUNT:
            amount_right = right
        if column != TRANSACTION_COL_TAG:
            last_non_tag_right = right
        x = right
    if amount_right is not None:
        return amount_right
    return last_non_tag_right if last_non_tag_right > span_rect.left() else span_rect.right()


def _expense_text_from_major(expense_major: float) -> str:
    if expense_major <= 0:
        return ""
    return f"-{expense_major:.2f}"


def _format_header_income(income_raw: str, host: QWidget | None) -> str:
    text = (income_raw or "").strip()
    if not text:
        return ""
    formatted = format_amount(text)
    if not formatted.startswith("+") and not formatted.startswith("-"):
        formatted = f"+{formatted}"
    return f"Income: {_with_header_currency(formatted, host)}"


def _format_header_total(total_raw: str, host: QWidget | None, *, has_income: bool = False) -> str:
    text = (total_raw or "").strip()
    if not text:
        return ""
    # Stored as "-12.50"; show with the same amount formatting as the table.
    # Expense-only days keep "Total:"; with income, spell out Expenses so it is not net.
    label = "Expenses" if has_income else "Total"
    return f"{label}: {_with_header_currency(format_amount(text), host)}"


def _format_month_banner_label(month_key: str, *, is_current: bool) -> str:
    label = month_key
    parts = month_key.split("-")
    if len(parts) == _YYYY_MM_PARTS and parts[0].isdigit() and parts[1].isdigit():
        year = int(parts[0])
        month = int(parts[1])
        if 1 <= month <= _MONTHS_IN_YEAR:
            date = QDate(year, month, 1)
            label = QLocale(QLocale.Language.English).toString(date, "MMMM yyyy")
    if is_current:
        return f"Current month · {label}"
    return label


def _income_text_from_major(income_major: float) -> str:
    return f"{income_major:.2f}" if income_major > 0 else ""


def _income_totals_by_date(source: QAbstractItemModel) -> dict[str, float]:
    """Sum income major units per date from the current source row order."""
    totals: dict[str, float] = {}
    for row in range(source.rowCount()):
        date_value = source.index(row, TRANSACTION_COL_DATE).data(Qt.ItemDataRole.DisplayRole)
        date_str = "" if date_value is None else str(date_value)
        if not date_str:
            continue
        category = source.index(row, TRANSACTION_COL_CATEGORY).data(Qt.ItemDataRole.DisplayRole)
        if not is_income_category_display(str(category or "")):
            continue
        amount = source.index(row, TRANSACTION_COL_AMOUNT).data(Qt.ItemDataRole.DisplayRole)
        totals[date_str] = totals.get(date_str, 0.0) + parse_transaction_amount_display(str(amount or ""))
    return totals


def _month_flow_totals(
    source: QAbstractItemModel,
    income_by_date: dict[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    """Return `(expense_by_month, income_by_month)` from day totals and income map."""
    expense_by_month: dict[str, float] = {}
    income_by_month: dict[str, float] = {}
    seen_dates: set[str] = set()
    for row in range(source.rowCount()):
        date_value = source.index(row, TRANSACTION_COL_DATE).data(Qt.ItemDataRole.DisplayRole)
        date_str = "" if date_value is None else str(date_value).strip()
        month = _month_key(date_str)
        if not month:
            continue
        if date_str not in seen_dates:
            seen_dates.add(date_str)
            total_value = source.index(row, TRANSACTION_COL_TOTAL_PER_DAY).data(Qt.ItemDataRole.DisplayRole)
            expense = abs(parse_transaction_amount_display(str(total_value or "")))
            if expense > 0:
                expense_by_month[month] = expense_by_month.get(month, 0.0) + expense
            income = income_by_date.get(date_str, 0.0)
            if income > 0:
                income_by_month[month] = income_by_month.get(month, 0.0) + income
    return expense_by_month, income_by_month


def _month_header_fill(fluent: Any) -> QColor:
    """Neutral wash for month banners — not soft-blue selection chrome."""
    if getattr(fluent, "dark", False):
        wash = QColor(255, 255, 255, _MONTH_WASH_ALPHA_DARK)
        return mix(fluent.window_bg, wash)
    return QColor(HAIRLINE)


def _month_key(date_str: str) -> str:
    text = (date_str or "").strip()
    return text[:_YYYY_MM_PREFIX_LEN] if len(text) >= _YYYY_MM_PREFIX_LEN and text[4] == "-" else ""


def _with_header_currency(formatted: str, host: QWidget | None) -> str:
    symbol = ""
    if host is not None:
        getter = getattr(host.window(), "_get_default_currency_symbol", None)
        if callable(getter):
            try:
                symbol = str(getter() or "")
            except Exception:
                symbol = ""
    return with_currency(formatted, symbol) if symbol else formatted
