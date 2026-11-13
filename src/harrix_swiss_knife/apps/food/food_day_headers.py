"""Day and month group headers for the Food Tracker food log table.

Inserts display-only header rows above each consecutive date run (newest-first),
plus month summary banners with optional month kcal totals. Headers are not log rows.

"""

from __future__ import annotations

from typing import Any, overload

from PySide6.QtCore import (
    QAbstractItemModel,
    QAbstractProxyModel,
    QDate,
    QEvent,
    QLocale,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QRect,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QFontMetrics, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QAbstractItemDelegate, QStyledItemDelegate, QStyleOptionViewItem, QTableView, QWidget

from harrix_swiss_knife.apps.common.day_bands import DAY_BAND_ROLE, day_band_color
from harrix_swiss_knife.apps.common.ui_chrome import HAIRLINE
from harrix_swiss_knife.apps.food.day_macros import (
    CalorieThresholds,
    DayMacrosStatus,
    calorie_band_rgb,
    kcal_tone,
)
from harrix_swiss_knife.apps.food.delegates.day_total_delegate import macros_button_appearance
from harrix_swiss_knife.apps.food.delegates.is_drink_delegate import parse_is_drink_cell
from harrix_swiss_knife.apps.food.food_log_calories import (
    FOOD_LOG_COL_CALORIES,
    FOOD_LOG_COL_DATE,
    FOOD_LOG_COL_WEIGHT,
    calculate_food_log_calories,
    parse_food_log_number,
)
from harrix_swiss_knife.fluent.theme import mix, palette_for

FOOD_LOG_COL_IS_DRINK = 1

IS_DAY_HEADER_ROLE = Qt.ItemDataRole.UserRole + 720
DAY_HEADER_DATE_ROLE = Qt.ItemDataRole.UserRole + 721
IS_MONTH_HEADER_ROLE = Qt.ItemDataRole.UserRole + 722
DAY_HEADER_IS_CURRENT_MONTH_ROLE = Qt.ItemDataRole.UserRole + 723
DAY_HEADER_KCAL_ROLE = Qt.ItemDataRole.UserRole + 724
DAY_HEADER_DRINKS_ROLE = Qt.ItemDataRole.UserRole + 725
DAY_HEADER_MACROS_STATUS_ROLE = Qt.ItemDataRole.UserRole + 726
DAY_HEADER_THRESHOLD_RGB_ROLE = Qt.ItemDataRole.UserRole + 727

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
_CHIP_SIZE = 8
_CHIP_RADIUS = 2
_ELEMENT_GAP = 6
_BUTTON_HEIGHT = 22
_BUTTON_RADIUS = 4
_BUTTON_TEXT_PAD = 6
_BUTTON_BORDER = 1
_MIN_BUTTON_SIZE = 8
_RGB_COMPONENTS = 3
_COSMETIC_ROLES = frozenset(
    {
        int(Qt.ItemDataRole.BackgroundRole),
        int(Qt.ItemDataRole.ForegroundRole),
        int(Qt.ItemDataRole.FontRole),
        int(Qt.ItemDataRole.DecorationRole),
        int(DAY_BAND_ROLE),
    },
)


class FoodDayHeaderDelegate(QStyledItemDelegate):
    """Paint day/month headers: date left; kcal, drinks, band chip, macros button on day rows."""

    macros_requested = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize delegate and enable macros-button hover tracking on the food log view."""
        super().__init__(parent)
        self._hover_index = QPersistentModelIndex()
        if isinstance(parent, QTableView):
            parent.viewport().setMouseTracking(True)
            parent.viewport().installEventFilter(self)

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Emit `macros_requested` when the day-header macros chip is clicked."""
        if not bool(index.data(IS_DAY_HEADER_ROLE)):
            return super().editorEvent(event, model, option, index)
        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            day = _day_key(index.data(DAY_HEADER_DATE_ROLE))
            button = _header_macros_button_rect(option.rect, option.font, index)
            if day and button.contains(event.position().toPoint()):
                self.macros_requested.emit(day)
                return True
        return super().editorEvent(event, model, option, index)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track pointer hover over the day-header macros button."""
        view = self.parent()
        if isinstance(view, QTableView) and watched is view.viewport():
            self._update_hover(view, event)
        return super().eventFilter(watched, event)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw day/month header chrome, or fall through for ordinary cells."""
        is_day = bool(index.data(IS_DAY_HEADER_ROLE))
        is_month = bool(index.data(IS_MONTH_HEADER_ROLE))
        if not is_day and not is_month:
            super().paint(painter, option, index)
            return

        date_text = str(index.data(DAY_HEADER_DATE_ROLE) or "")
        host = option.widget if isinstance(option.widget, QWidget) else None
        fluent = palette_for(host)
        fill = index.data(Qt.ItemDataRole.BackgroundRole)
        if isinstance(fill, QColor):
            background = fill
        elif is_month:
            background = _month_header_fill(fluent)
        else:
            background = day_band_color(0)
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
        metrics_font = QFont(option.font)
        metrics_font.setBold(True)
        if metrics_font.pointSize() > 0:
            metrics_font.setPointSize(metrics_font.pointSize() + (2 if is_month else 1))
        date_metrics = QFontMetrics(date_font)
        metrics = QFontMetrics(metrics_font)

        text_left = option.rect.left() + _HEADER_PAD_X
        text_right = option.rect.right() - _HEADER_PAD_X
        text_rect = QRect(text_left, option.rect.top(), text_right - text_left, option.rect.height())

        if is_month:
            kcal_display = _format_month_kcal_label(str(index.data(DAY_HEADER_KCAL_ROLE) or ""))
            kcal_width = metrics.horizontalAdvance(kcal_display) if kcal_display else 0
            date_width = max(0, text_rect.width() - kcal_width - 12)
            painter.setFont(date_font)
            painter.setPen(ink)
            painter.drawText(
                text_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                date_metrics.elidedText(date_text, Qt.TextElideMode.ElideRight, date_width),
            )
            if kcal_display:
                painter.setFont(metrics_font)
                painter.setPen(ink)
                kcal_rect = QRect(text_rect.right() - kcal_width, text_rect.top(), kcal_width, text_rect.height())
                painter.drawText(
                    kcal_rect,
                    int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                    kcal_display,
                )
            painter.restore()
            return

        segments, chip_rect, button = _day_header_right_layout(option.rect, option.font, index)
        right_width = sum(width for _text, width in segments)
        if chip_rect is not None:
            right_width += _CHIP_SIZE + _ELEMENT_GAP
        right_width += button.width()
        if button.width() > 0 and (segments or chip_rect is not None):
            right_width += _ELEMENT_GAP
        date_width = max(0, text_rect.width() - right_width - 12)

        painter.setFont(date_font)
        painter.setPen(muted)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            date_metrics.elidedText(date_text, Qt.TextElideMode.ElideRight, date_width),
        )

        cursor_x = button.left() - _ELEMENT_GAP if button.width() > 0 else text_rect.right()
        if chip_rect is not None:
            chip_color = _threshold_color(index.data(DAY_HEADER_THRESHOLD_RGB_ROLE))
            if chip_color is not None:
                painter.save()
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(chip_color)
                painter.drawRoundedRect(chip_rect, _CHIP_RADIUS, _CHIP_RADIUS)
                painter.restore()
            cursor_x = chip_rect.left() - _ELEMENT_GAP

        painter.setFont(metrics_font)
        painter.setPen(ink)
        for segment_text, segment_width in reversed(segments):
            if not segment_text:
                continue
            segment_rect = QRect(cursor_x - segment_width, text_rect.top(), segment_width, text_rect.height())
            painter.drawText(
                segment_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                segment_text,
            )
            cursor_x = segment_rect.left() - _ELEMENT_GAP

        if button.width() >= _MIN_BUTTON_SIZE:
            status = _macros_status_from_role(index.data(DAY_HEADER_MACROS_STATUS_ROLE))
            appearance = macros_button_appearance(status)
            button_font = QFont(option.font)
            button_font.setBold(False)
            self._paint_macros_button(
                painter,
                button,
                appearance,
                button_font,
                hovered=self._hover_index.isValid() and self._hover_index == index,
            )

        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Make month banners slightly taller than day headers."""
        hint = super().sizeHint(option, index)
        min_height = hint.height()
        if bool(index.data(IS_MONTH_HEADER_ROLE)):
            min_height = max(min_height, _MONTH_MIN_HEIGHT)
        elif bool(index.data(IS_DAY_HEADER_ROLE)):
            min_height = max(min_height, _BUTTON_HEIGHT + 8)
        return QSize(hint.width(), min_height)

    def _paint_macros_button(
        self,
        painter: QPainter,
        rect: QRect,
        appearance: Any,
        font: QFont,
        *,
        hovered: bool,
    ) -> None:
        if rect.width() < _MIN_BUTTON_SIZE or rect.height() < _MIN_BUTTON_SIZE:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setPen(QPen(appearance.border, _BUTTON_BORDER))
        painter.setBrush(appearance.hover_background if hovered else appearance.background)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), _BUTTON_RADIUS, _BUTTON_RADIUS)
        painter.setFont(font)
        painter.setPen(appearance.text)
        label_width = max(0, rect.width() - (2 * _BUTTON_TEXT_PAD))
        label = QFontMetrics(font).elidedText(appearance.label, Qt.TextElideMode.ElideRight, label_width)
        painter.drawText(
            rect.adjusted(_BUTTON_TEXT_PAD, 0, -_BUTTON_TEXT_PAD, 0),
            int(Qt.AlignmentFlag.AlignCenter),
            label,
        )
        painter.restore()

    def _set_button_hover(self, view: QTableView, index: QModelIndex) -> None:
        if (self._hover_index.isValid() and self._hover_index == index) or (
            not self._hover_index.isValid() and not index.isValid()
        ):
            return
        previous_row = self._hover_index.row()
        had_hover = self._hover_index.isValid()
        self._hover_index = QPersistentModelIndex(index) if index.isValid() else QPersistentModelIndex()
        viewport = view.viewport()
        model = view.model()
        if had_hover and model is not None:
            viewport.update(view.visualRect(model.index(previous_row, 0)))
        if index.isValid():
            viewport.update(view.visualRect(index))
        viewport.setCursor(Qt.CursorShape.PointingHandCursor if index.isValid() else Qt.CursorShape.ArrowCursor)

    def _update_hover(self, view: QTableView, event: QEvent) -> None:
        if event.type() == QEvent.Type.Leave:
            self._set_button_hover(view, QModelIndex())
            return
        if event.type() != QEvent.Type.MouseMove or not isinstance(event, QMouseEvent):
            return
        pos = event.position().toPoint()
        index = view.indexAt(pos)
        if not index.isValid() or index.column() != 0 or not bool(index.data(IS_DAY_HEADER_ROLE)):
            self._set_button_hover(view, QModelIndex())
            return
        _segments, _chip, button = _day_header_right_layout(view.visualRect(index), view.font(), index)
        if _day_key(index.data(DAY_HEADER_DATE_ROLE)) and button.contains(pos):
            self._set_button_hover(view, index)
        else:
            self._set_button_hover(view, QModelIndex())


class FoodDayHeaderProxy(QAbstractProxyModel):
    """Proxy that inserts day and month header rows into the food log list."""

    mapping_reset = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        """Create an empty day-header proxy."""
        super().__init__(parent)
        self._proxy_rows: list[int] = []
        self._header_dates: dict[int, str] = {}
        self._header_day_keys: dict[int, str] = {}
        self._header_kcal: dict[int, str] = {}
        self._header_drinks: dict[int, str] = {}
        self._header_macros: dict[int, str] = {}
        self._header_threshold: dict[int, object] = {}
        self._header_tooltips: dict[int, str] = {}
        self._header_bands: dict[int, int] = {}
        self._header_month_rows: set[int] = set()
        self._header_current_month_rows: set[int] = set()
        self._source_to_proxy: dict[int, int] = {}
        self._rebuild_scheduled = False
        self._macros_statuses: dict[str, DayMacrosStatus] = {}
        self._calorie_thresholds = CalorieThresholds()
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
            if role == DAY_HEADER_KCAL_ROLE:
                return self._header_kcal.get(proxy_row, "")
            if role == DAY_HEADER_DRINKS_ROLE:
                return self._header_drinks.get(proxy_row, "")
            if role == DAY_HEADER_MACROS_STATUS_ROLE:
                return self._header_macros.get(proxy_row, "")
            if role == DAY_HEADER_THRESHOLD_RGB_ROLE:
                return self._header_threshold.get(proxy_row)
            if role == Qt.ItemDataRole.ToolTipRole:
                return self._header_tooltips.get(proxy_row)
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

    def set_calorie_thresholds(self, thresholds: CalorieThresholds) -> None:
        """Replace configured kcal bands used for header threshold chips."""
        self._calorie_thresholds = thresholds
        self._refresh_day_header_metadata()

    def set_macros_statuses(self, statuses: dict[str, DayMacrosStatus]) -> None:
        """Replace cached day-macros button states for header rows."""
        self._macros_statuses = dict(statuses)
        self._refresh_day_header_metadata()

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
        kcal: float,
        drinks_grams: float,
        band_index: int,
    ) -> None:
        header_row = len(self._proxy_rows)
        day_key = _day_key(date_str)
        self._proxy_rows.append(_PROXY_DAY_HEADER)
        self._header_dates[header_row] = date_str
        self._header_day_keys[header_row] = day_key
        self._header_kcal[header_row] = f"{kcal:.1f}"
        self._header_drinks[header_row] = f"{drinks_grams:.1f}" if drinks_grams > 0 else ""
        self._header_bands[header_row] = band_index
        self._apply_day_header_metadata(header_row, kcal=kcal, day_key=day_key)

    def _append_month_header(self, *, month_key: str, kcal_total: float, is_current: bool) -> None:
        header_row = len(self._proxy_rows)
        self._proxy_rows.append(_PROXY_MONTH_HEADER)
        self._header_month_rows.add(header_row)
        if is_current:
            self._header_current_month_rows.add(header_row)
        self._header_dates[header_row] = _format_month_banner_label(month_key, is_current=is_current)
        self._header_kcal[header_row] = f"{kcal_total:.1f}" if kcal_total > 0 else ""
        self._header_bands[header_row] = 0

    def _apply_day_header_metadata(self, proxy_row: int, *, kcal: float, day_key: str) -> None:
        status = self._macros_statuses.get(day_key, DayMacrosStatus.MISSING)
        self._header_macros[proxy_row] = status.value
        rgb = calorie_band_rgb(kcal, self._calorie_thresholds)
        self._header_threshold[proxy_row] = rgb
        self._header_tooltips[proxy_row] = _calorie_threshold_tooltip(kcal, self._calorie_thresholds)

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
        rebuild_cols = {
            FOOD_LOG_COL_IS_DRINK,
            FOOD_LOG_COL_WEIGHT,
            FOOD_LOG_COL_CALORIES,
            FOOD_LOG_COL_DATE,
        }
        if any(top_left.column() <= col <= bottom_right.column() for col in rebuild_cols):
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
        self._header_day_keys = {}
        self._header_kcal = {}
        self._header_drinks = {}
        self._header_macros = {}
        self._header_threshold = {}
        self._header_tooltips = {}
        self._header_bands = {}
        self._header_month_rows = set()
        self._header_current_month_rows = set()
        self._source_to_proxy = {}
        source = self.sourceModel()
        if source is None:
            self.endResetModel()
            self.mapping_reset.emit()
            return

        kcal_by_date, drinks_by_date, kcal_by_month = _food_day_totals(source)
        current_month = self._current_month_key()
        current_kcal = kcal_by_month.get(current_month, 0.0)
        if source.rowCount() > 0 and current_kcal > 0:
            self._append_month_header(month_key=current_month, kcal_total=current_kcal, is_current=True)

        previous_date: object = object()
        previous_month: str | None = None
        band_index = 0
        for source_row in range(source.rowCount()):
            date_value = source.index(source_row, FOOD_LOG_COL_DATE).data(Qt.ItemDataRole.DisplayRole)
            date_str = "" if date_value is None else str(date_value).strip()
            month_key = _month_key(date_str)
            if date_str and date_str != previous_date:
                day_key = _day_key(date_str)
                if month_key and month_key != previous_month:
                    if month_key != current_month:
                        self._append_month_header(
                            month_key=month_key,
                            kcal_total=kcal_by_month.get(month_key, 0.0),
                            is_current=False,
                        )
                    previous_month = month_key
                self._append_day_header(
                    date_str=date_str,
                    kcal=kcal_by_date.get(day_key, 0.0),
                    drinks_grams=drinks_by_date.get(day_key, 0.0),
                    band_index=band_index,
                )
                band_index = 1 - band_index
                previous_date = date_str
            self._source_to_proxy[source_row] = len(self._proxy_rows)
            self._proxy_rows.append(source_row)
        self.endResetModel()
        self.mapping_reset.emit()

    def _refresh_day_header_metadata(self) -> None:
        if not self._header_day_keys:
            return
        columns = max(self.columnCount() - 1, 0)
        roles = [
            int(DAY_HEADER_MACROS_STATUS_ROLE),
            int(DAY_HEADER_THRESHOLD_RGB_ROLE),
            int(Qt.ItemDataRole.ToolTipRole),
        ]
        for proxy_row, day_key in self._header_day_keys.items():
            kcal_text = self._header_kcal.get(proxy_row, "0")
            try:
                kcal = float(kcal_text)
            except ValueError:
                kcal = 0.0
            self._apply_day_header_metadata(proxy_row, kcal=kcal, day_key=day_key)
            left = self.index(proxy_row, 0)
            right = self.index(proxy_row, columns)
            self.dataChanged.emit(left, right, roles)

    def _schedule_rebuild(self) -> None:
        if self._rebuild_scheduled:
            return
        self._rebuild_scheduled = True
        QTimer.singleShot(0, self._rebuild_mapping)


class _FoodDayHeaderOrDelegate(QStyledItemDelegate):
    """Paint day/month headers; otherwise forward to the column-0 delegate."""

    def __init__(self, inner: QAbstractItemDelegate, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._inner = inner
        self._header = FoodDayHeaderDelegate(parent)

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        return self._inner.createEditor(parent, option, index)

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if bool(index.data(IS_DAY_HEADER_ROLE)) or bool(index.data(IS_MONTH_HEADER_ROLE)):
            return self._header.editorEvent(event, model, option, index)
        return self._inner.editorEvent(event, model, option, index)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if self._header.eventFilter(watched, event):
            return True
        return super().eventFilter(watched, event)

    @property
    def food_day_header_delegate(self) -> FoodDayHeaderDelegate:
        """Return the inner header delegate (for `macros_requested` wiring)."""
        return self._header

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


def apply_food_day_header_spans(view: QTableView) -> None:
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


def food_day_header_delegate_for_view(view: QTableView) -> FoodDayHeaderDelegate | None:
    """Return the day-header delegate installed on column 0, if any."""
    delegate = view.itemDelegateForColumn(0)
    if isinstance(delegate, FoodDayHeaderDelegate):
        return delegate
    if isinstance(delegate, _FoodDayHeaderOrDelegate):
        return delegate.food_day_header_delegate
    return None


def install_food_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> FoodDayHeaderProxy:
    """Wrap `sort_proxy` with day/month headers and show it on `view`."""
    existing = view.model()
    if isinstance(existing, FoodDayHeaderProxy) and existing.sourceModel() is sort_proxy:
        existing.rebuild()
        apply_food_day_header_spans(view)
        return existing

    proxy = FoodDayHeaderProxy(view)
    proxy.setSourceModel(sort_proxy)
    view.setModel(proxy)

    def _on_mapping_reset() -> None:
        apply_food_day_header_spans(view)

    proxy.mapping_reset.connect(_on_mapping_reset)
    apply_food_day_header_spans(view)

    description_delegate = view.itemDelegateForColumn(0)
    if isinstance(description_delegate, (FoodDayHeaderDelegate, _FoodDayHeaderOrDelegate)):
        return proxy
    if description_delegate is not None:
        view.setItemDelegateForColumn(0, _FoodDayHeaderOrDelegate(description_delegate, view))
    else:
        view.setItemDelegateForColumn(0, FoodDayHeaderDelegate(view))
    return proxy


def is_food_day_or_month_header(index: QModelIndex) -> bool:
    """Return whether `index` is a food log day or month group header row."""
    if not index.isValid():
        return False
    return bool(index.data(IS_DAY_HEADER_ROLE)) or bool(index.data(IS_MONTH_HEADER_ROLE))


def map_food_log_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]:
    """Walk proxy layers until the ultimate source model index."""
    model: Any = index.model()
    current = index
    while isinstance(model, QAbstractProxyModel):
        current = model.mapToSource(current)
        if not current.isValid():
            return current, model.sourceModel()
        model = model.sourceModel()
    return current, model


def ultimate_food_log_source(model: Any) -> Any:
    """Return the innermost model under nested proxies."""
    current = model
    while isinstance(current, QAbstractProxyModel):
        current = current.sourceModel()
    return current


def _calorie_threshold_tooltip(kcal: float, thresholds: CalorieThresholds) -> str:
    tone = kcal_tone(kcal, thresholds)
    if tone == "good":
        return f"Daily total {kcal:.1f} kcal — within or below low band (≤ {thresholds.low:.0f} kcal)"
    if tone == "warn":
        if kcal <= thresholds.medium_low:
            return f"Daily total {kcal:.1f} kcal — medium-low band (≤ {thresholds.medium_low:.0f} kcal)"
        return f"Daily total {kcal:.1f} kcal — medium-high band (≤ {thresholds.medium_high:.0f} kcal)"
    return f"Daily total {kcal:.1f} kcal — above medium-high band (> {thresholds.medium_high:.0f} kcal)"


def _day_header_right_layout(
    span_rect: QRect,
    font: QFont,
    index: QModelIndex | QPersistentModelIndex,
) -> tuple[list[tuple[str, int]], QRect | None, QRect]:
    """Return text segments, optional threshold chip rect, and macros button rect."""
    metrics = QFontMetrics(font)
    segments: list[tuple[str, int]] = []
    kcal_raw = str(index.data(DAY_HEADER_KCAL_ROLE) or "").strip()
    if kcal_raw:
        try:
            kcal_value = float(kcal_raw)
        except ValueError:
            kcal_value = 0.0
        kcal_text = f"{kcal_value:.1f} kcal"
        segments.append((kcal_text, metrics.horizontalAdvance(kcal_text)))

    drinks_raw = str(index.data(DAY_HEADER_DRINKS_ROLE) or "").strip()
    if drinks_raw:
        try:
            drinks_grams = float(drinks_raw)
        except ValueError:
            drinks_grams = 0.0
        if drinks_grams > 0:
            liters_text = f"{drinks_grams / 1000:.1f} L"
            segments.append((liters_text, metrics.horizontalAdvance(liters_text)))

    button = _header_macros_button_rect(span_rect, font, index)
    chip_rect: QRect | None = None
    if _threshold_color(index.data(DAY_HEADER_THRESHOLD_RGB_ROLE)) is not None:
        cursor_x = button.left() - _ELEMENT_GAP
        chip_top = span_rect.top() + max(0, (span_rect.height() - _CHIP_SIZE) // 2)
        chip_rect = QRect(cursor_x - _CHIP_SIZE, chip_top, _CHIP_SIZE, _CHIP_SIZE)
    return segments, chip_rect, button


def _day_key(value: object) -> str:
    text = str(value or "").strip()
    return text[:10]


def _food_day_totals(
    source: QAbstractItemModel,
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """Return `(kcal_by_date, drinks_grams_by_date, kcal_by_month)` from the source model."""
    kcal_by_date: dict[str, float] = {}
    drinks_by_date: dict[str, float] = {}
    kcal_by_month: dict[str, float] = {}
    for row in range(source.rowCount()):
        date_value = source.index(row, FOOD_LOG_COL_DATE).data(Qt.ItemDataRole.DisplayRole)
        date_str = "" if date_value is None else str(date_value).strip()
        day_key = _day_key(date_str)
        if not day_key:
            continue
        weight = parse_food_log_number(
            source.index(row, FOOD_LOG_COL_WEIGHT).data(Qt.ItemDataRole.DisplayRole),
        )
        kcal_per_100 = parse_food_log_number(
            source.index(row, FOOD_LOG_COL_CALORIES).data(Qt.ItemDataRole.DisplayRole),
        )
        kcal = calculate_food_log_calories(weight, kcal_per_100)
        kcal_by_date[day_key] = kcal_by_date.get(day_key, 0.0) + kcal
        month = _month_key(day_key)
        if month:
            kcal_by_month[month] = kcal_by_month.get(month, 0.0) + kcal
        is_drink = parse_is_drink_cell(
            source.index(row, FOOD_LOG_COL_IS_DRINK).data(Qt.ItemDataRole.DisplayRole),
        )
        if is_drink and weight is not None and weight > 0:
            drinks_by_date[day_key] = drinks_by_date.get(day_key, 0.0) + float(weight)
    return kcal_by_date, drinks_by_date, kcal_by_month


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


def _format_month_kcal_label(kcal_raw: str) -> str:
    text = (kcal_raw or "").strip()
    if not text:
        return ""
    try:
        value = float(text)
    except ValueError:
        return f"{text} kcal"
    return f"{value:.1f} kcal"


def _header_macros_button_rect(
    span_rect: QRect,
    font: QFont,
    index: QModelIndex | QPersistentModelIndex,
) -> QRect:
    """Return the macros button bounds on the right edge of a day header row."""
    status = _macros_status_from_role(index.data(DAY_HEADER_MACROS_STATUS_ROLE))
    appearance = macros_button_appearance(status)
    button_font = QFont(font)
    button_font.setBold(False)
    label_width = QFontMetrics(button_font).horizontalAdvance(appearance.label)
    width = label_width + (2 * _BUTTON_TEXT_PAD) + _BUTTON_BORDER
    top = span_rect.top() + max(0, (span_rect.height() - _BUTTON_HEIGHT) // 2)
    left = span_rect.right() - _HEADER_PAD_X - width
    return QRect(left, top, width, _BUTTON_HEIGHT)


def _macros_status_from_role(value: object) -> DayMacrosStatus:
    text = str(value or "").strip()
    if not text:
        return DayMacrosStatus.MISSING
    try:
        return DayMacrosStatus(text)
    except ValueError:
        return DayMacrosStatus.MISSING


def _month_header_fill(fluent: Any) -> QColor:
    """Neutral wash for month banners — not soft-blue selection chrome."""
    if getattr(fluent, "dark", False):
        wash = QColor(255, 255, 255, _MONTH_WASH_ALPHA_DARK)
        return mix(fluent.window_bg, wash)
    return QColor(HAIRLINE)


def _month_key(date_str: str) -> str:
    text = (date_str or "").strip()
    return text[:_YYYY_MM_PREFIX_LEN] if len(text) >= _YYYY_MM_PREFIX_LEN and text[4] == "-" else ""


def _threshold_color(value: object) -> QColor | None:
    if isinstance(value, QColor):
        return value
    if isinstance(value, tuple) and len(value) >= _RGB_COMPONENTS:
        try:
            red, green, blue = int(value[0]), int(value[1]), int(value[2])
        except (TypeError, ValueError):
            return None
        return QColor(red, green, blue)
    return None
