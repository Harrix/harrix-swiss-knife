"""Day and month group headers for the Fitness process (Sets) table.

Inserts display-only header rows above each consecutive date run (newest-first),
plus month summary banners with set counts. Headers are not process rows.

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
from harrix_swiss_knife.fluent.theme import mix, palette_for

if TYPE_CHECKING:
    from PySide6.QtCore import QPersistentModelIndex

PROCESS_COL_DATE = 3

IS_DAY_HEADER_ROLE = Qt.ItemDataRole.UserRole + 620
DAY_HEADER_DATE_ROLE = Qt.ItemDataRole.UserRole + 621
DAY_HEADER_SETS_ROLE = Qt.ItemDataRole.UserRole + 622
IS_MONTH_HEADER_ROLE = Qt.ItemDataRole.UserRole + 623
DAY_HEADER_IS_CURRENT_MONTH_ROLE = Qt.ItemDataRole.UserRole + 624

_HEADER_PAD_X = 8
_SEPARATOR_ALPHA = 90
_MONTH_SEPARATOR_ALPHA = 160
_MONTH_MIN_HEIGHT = 36
_MONTH_WASH_ALPHA_DARK = 28
_PROXY_DAY_HEADER = -1
_PROXY_MONTH_HEADER = -2
_YYYY_MM_PARTS = 2
_MONTHS_IN_YEAR = 12
_YYYY_MM_PREFIX_LEN = 7
_COSMETIC_ROLES = frozenset(
    {
        int(Qt.ItemDataRole.BackgroundRole),
        int(Qt.ItemDataRole.ForegroundRole),
        int(Qt.ItemDataRole.FontRole),
        int(Qt.ItemDataRole.DecorationRole),
        int(DAY_BAND_ROLE),
    },
)


class ProcessDayHeaderDelegate(QStyledItemDelegate):
    """Paint day/month headers (label left, Sets count right) for spanned rows."""

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
        sets_raw = str(index.data(DAY_HEADER_SETS_ROLE) or "")
        host = option.widget if isinstance(option.widget, QWidget) else None
        fluent = palette_for(host)
        fill = index.data(Qt.ItemDataRole.BackgroundRole)
        if isinstance(fill, QColor):
            background = fill
        elif is_month:
            background = _month_header_fill(fluent)
        else:
            background = mix(fluent.window_bg, fluent.card_bg)
        ink = mix(fluent.window_bg, fluent.text_primary)
        muted = mix(fluent.window_bg, fluent.text_secondary)
        hairline = mix(fluent.window_bg, fluent.divider)
        hairline.setAlpha(_MONTH_SEPARATOR_ALPHA if is_month else _SEPARATOR_ALPHA)

        painter.save()
        painter.fillRect(option.rect, background)
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

        sets_display = _format_sets_label(sets_raw)
        sets_width = total_metrics.horizontalAdvance(sets_display) if sets_display else 0
        text_left = option.rect.left() + _HEADER_PAD_X
        text_right = max(text_left, option.rect.right() - _HEADER_PAD_X)
        text_rect = QRect(text_left, option.rect.top(), text_right - text_left, option.rect.height())
        date_width = max(0, text_rect.width() - sets_width - 12)

        painter.setFont(date_font)
        painter.setPen(ink if is_month else muted)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            date_metrics.elidedText(date_text, Qt.TextElideMode.ElideRight, date_width),
        )
        if sets_display:
            painter.setFont(total_font)
            painter.setPen(ink)
            sets_rect = QRect(
                text_rect.right() - sets_width,
                text_rect.top(),
                sets_width,
                text_rect.height(),
            )
            painter.drawText(
                sets_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                sets_display,
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


class ProcessDayHeaderProxy(QAbstractProxyModel):
    """Proxy that inserts day and month header rows into the process list."""

    mapping_reset = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        """Create an empty day-header proxy."""
        super().__init__(parent)
        self._proxy_rows: list[int] = []
        self._header_dates: dict[int, str] = {}
        self._header_sets: dict[int, str] = {}
        self._header_bands: dict[int, int] = {}
        self._header_month_rows: set[int] = set()
        self._header_current_month_rows: set[int] = set()
        self._source_to_proxy: dict[int, int] = {}
        self._rebuild_scheduled = False
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
            if role == DAY_HEADER_SETS_ROLE:
                return self._header_sets.get(proxy_row, "")
            if role == Qt.ItemDataRole.DisplayRole:
                return self._header_dates.get(proxy_row, "") if index.column() == 0 else ""
            if role == Qt.ItemDataRole.BackgroundRole:
                if is_month:
                    return _month_header_fill(palette_for(None))
                return day_band_color(self._header_bands.get(proxy_row, 0))
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
                    return _month_header_fill(palette_for(None))
                return day_band_color(self._header_bands.get(section, 0))
            return None
        return source.headerData(self._proxy_rows[section], orientation, role)

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
        return source.index(self._proxy_rows[proxy_index.row()], proxy_index.column())

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

    def _append_day_header(self, *, date_str: str, sets_count: int, band_index: int) -> None:
        header_row = len(self._proxy_rows)
        self._proxy_rows.append(_PROXY_DAY_HEADER)
        self._header_dates[header_row] = date_str
        self._header_sets[header_row] = str(sets_count)
        self._header_bands[header_row] = band_index

    def _append_month_header(self, *, month_key: str, sets_count: int, is_current: bool) -> None:
        header_row = len(self._proxy_rows)
        self._proxy_rows.append(_PROXY_MONTH_HEADER)
        self._header_month_rows.add(header_row)
        if is_current:
            self._header_current_month_rows.add(header_row)
        self._header_dates[header_row] = _format_month_banner_label(month_key, is_current=is_current)
        self._header_sets[header_row] = str(sets_count)
        self._header_bands[header_row] = 0

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
        if role_values and set(role_values) <= _COSMETIC_ROLES:
            self._forward_source_data_changed(top_left, bottom_right, role_values)
            return
        if top_left.column() <= PROCESS_COL_DATE <= bottom_right.column():
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
        self._header_sets = {}
        self._header_bands = {}
        self._header_month_rows = set()
        self._header_current_month_rows = set()
        self._source_to_proxy = {}
        source = self.sourceModel()
        if source is None:
            self.endResetModel()
            self.mapping_reset.emit()
            return

        sets_by_date, sets_by_month = _sets_counts(source)
        current_month = self._current_month_key()
        current_sets = sets_by_month.get(current_month, 0)
        if source.rowCount() > 0 and current_sets > 0:
            self._append_month_header(month_key=current_month, sets_count=current_sets, is_current=True)

        previous_date: object = object()
        previous_month: str | None = None
        band_index = 0
        for source_row in range(source.rowCount()):
            date_value = source.index(source_row, PROCESS_COL_DATE).data(Qt.ItemDataRole.DisplayRole)
            date_str = "" if date_value is None else str(date_value).strip()
            month_key = _month_key(date_str)
            if date_str and date_str != previous_date:
                if month_key and month_key != previous_month:
                    if month_key != current_month:
                        self._append_month_header(
                            month_key=month_key,
                            sets_count=sets_by_month.get(month_key, 0),
                            is_current=False,
                        )
                    previous_month = month_key
                self._append_day_header(
                    date_str=date_str,
                    sets_count=sets_by_date.get(date_str, 0),
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


class _ProcessDayHeaderOrDelegate(QStyledItemDelegate):
    """Paint day/month headers; otherwise forward to the exercise-name delegate."""

    def __init__(self, inner: QAbstractItemDelegate, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._inner = inner
        self._header = ProcessDayHeaderDelegate(parent)

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


def apply_process_day_header_spans(view: QTableView) -> None:
    """Span each day/month header row across all columns."""
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


def install_process_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> ProcessDayHeaderProxy:
    """Wrap `sort_proxy` with day/month headers and show it on `view`."""
    existing = view.model()
    if isinstance(existing, ProcessDayHeaderProxy) and existing.sourceModel() is sort_proxy:
        existing.rebuild()
        apply_process_day_header_spans(view)
        return existing

    proxy = ProcessDayHeaderProxy(view)
    proxy.setSourceModel(sort_proxy)
    view.setModel(proxy)

    def _on_mapping_reset() -> None:
        apply_process_day_header_spans(view)

    proxy.mapping_reset.connect(_on_mapping_reset)
    apply_process_day_header_spans(view)

    description_delegate = view.itemDelegateForColumn(0)
    header_delegate: QAbstractItemDelegate = ProcessDayHeaderDelegate(view)
    if description_delegate is not None and not isinstance(description_delegate, ProcessDayHeaderDelegate):
        header_delegate = _ProcessDayHeaderOrDelegate(description_delegate, view)
    view.setItemDelegateForColumn(0, header_delegate)
    return proxy


def map_process_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]:
    """Walk proxy layers until the ultimate source model index."""
    model: Any = index.model()
    current = index
    while isinstance(model, QAbstractProxyModel):
        current = model.mapToSource(current)
        if not current.isValid():
            return current, model.sourceModel()
        model = model.sourceModel()
    return current, model


def ultimate_process_source(model: Any) -> Any:
    """Return the innermost model under nested proxies."""
    current = model
    while isinstance(current, QAbstractProxyModel):
        current = current.sourceModel()
    return current


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


def _format_sets_label(sets_raw: str) -> str:
    text = (sets_raw or "").strip()
    if not text:
        return ""
    try:
        count = int(text)
    except ValueError:
        return f"Sets: {text}"
    label = "set" if count == 1 else "sets"
    return f"{count} {label}"


def _month_header_fill(fluent: Any) -> QColor:
    """Neutral wash for month banners — not soft-blue selection chrome."""
    if getattr(fluent, "dark", False):
        wash = QColor(255, 255, 255, _MONTH_WASH_ALPHA_DARK)
        return mix(fluent.window_bg, wash)
    return QColor(HAIRLINE)


def _month_key(date_str: str) -> str:
    text = (date_str or "").strip()
    return text[:_YYYY_MM_PREFIX_LEN] if len(text) >= _YYYY_MM_PREFIX_LEN and text[4] == "-" else ""


def _sets_counts(source: QAbstractItemModel) -> tuple[dict[str, int], dict[str, int]]:
    """Return `(sets_by_date, sets_by_month)` from the process source model."""
    by_date: dict[str, int] = {}
    by_month: dict[str, int] = {}
    for row in range(source.rowCount()):
        date_value = source.index(row, PROCESS_COL_DATE).data(Qt.ItemDataRole.DisplayRole)
        date_str = "" if date_value is None else str(date_value).strip()
        if not date_str:
            continue
        by_date[date_str] = by_date.get(date_str, 0) + 1
        month = _month_key(date_str)
        if month:
            by_month[month] = by_month.get(month, 0) + 1
    return by_date, by_month
