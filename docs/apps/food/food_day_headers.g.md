---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_day_headers.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodDayHeaderDelegate`](#%EF%B8%8F-class-fooddayheaderdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🏛️ Class `FoodDayHeaderProxy`](#%EF%B8%8F-class-fooddayheaderproxy)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `columnCount`](#%EF%B8%8F-method-columncount)
  - [⚙️ Method `data`](#%EF%B8%8F-method-data)
  - [⚙️ Method `flags`](#%EF%B8%8F-method-flags)
  - [⚙️ Method `headerData`](#%EF%B8%8F-method-headerdata)
  - [⚙️ Method `index`](#%EF%B8%8F-method-index)
  - [⚙️ Method `mapFromSource`](#%EF%B8%8F-method-mapfromsource)
  - [⚙️ Method `mapToSource`](#%EF%B8%8F-method-maptosource)
  - [⚙️ Method `parent (overload)`](#%EF%B8%8F-method-parent-overload)
  - [⚙️ Method `parent (overload 2)`](#%EF%B8%8F-method-parent-overload-2)
  - [⚙️ Method `parent`](#%EF%B8%8F-method-parent)
  - [⚙️ Method `rebuild`](#%EF%B8%8F-method-rebuild)
  - [⚙️ Method `rowCount`](#%EF%B8%8F-method-rowcount)
  - [⚙️ Method `setSourceModel`](#%EF%B8%8F-method-setsourcemodel)
  - [⚙️ Method `set_calorie_thresholds`](#%EF%B8%8F-method-set_calorie_thresholds)
  - [⚙️ Method `set_macros_statuses`](#%EF%B8%8F-method-set_macros_statuses)
  - [⚙️ Method `sort`](#%EF%B8%8F-method-sort)
- [🔧 Function `apply_food_day_header_spans`](#-function-apply_food_day_header_spans)
- [🔧 Function `food_day_header_delegate_for_view`](#-function-food_day_header_delegate_for_view)
- [🔧 Function `install_food_day_headers`](#-function-install_food_day_headers)
- [🔧 Function `is_food_day_or_month_header`](#-function-is_food_day_or_month_header)
- [🔧 Function `map_food_log_index_to_source`](#-function-map_food_log_index_to_source)
- [🔧 Function `ultimate_food_log_source`](#-function-ultimate_food_log_source)

</details>

## 🏛️ Class `FoodDayHeaderDelegate`

```python
class FoodDayHeaderDelegate(QStyledItemDelegate)
```

Paint day/month headers: date left; kcal, drinks, band chip, macros button on day rows.

<details>
<summary>Code:</summary>

```python
class FoodDayHeaderDelegate(QStyledItemDelegate):

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
            layout = _day_header_chrome_layout(option.rect, option.font, index)
            if day and layout.button_rect.contains(event.position().toPoint()):
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
        # Month banners follow the painting host — avoid palette_for(None) light fills.
        if is_month:
            background = _month_header_fill(fluent)
        elif isinstance(fill, QColor):
            background = fill
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

        chrome = _day_header_chrome_layout(option.rect, option.font, index)
        date_width = max(0, text_rect.width() - chrome.right_block_width - 12)

        painter.setFont(date_font)
        painter.setPen(muted)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            date_metrics.elidedText(date_text, Qt.TextElideMode.ElideRight, date_width),
        )

        if chrome.summary_text and chrome.summary_rect.width() > 0:
            painter.setFont(metrics_font)
            painter.setPen(ink)
            painter.drawText(
                chrome.summary_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                QFontMetrics(metrics_font).elidedText(
                    chrome.summary_text,
                    Qt.TextElideMode.ElideRight,
                    chrome.summary_rect.width(),
                ),
            )

        if chrome.chip_rect is not None:
            chip_color = _threshold_color(index.data(DAY_HEADER_THRESHOLD_RGB_ROLE))
            if chip_color is not None:
                painter.save()
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(chip_color)
                painter.drawRoundedRect(chrome.chip_rect, _CHIP_RADIUS, _CHIP_RADIUS)
                painter.restore()

        if chrome.button_rect.width() >= _MIN_BUTTON_SIZE:
            status = _macros_status_from_role(index.data(DAY_HEADER_MACROS_STATUS_ROLE))
            appearance = macros_button_appearance(status)
            button_font = QFont(option.font)
            button_font.setBold(False)
            self._paint_macros_button(
                painter,
                chrome.button_rect,
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
        chrome = _day_header_chrome_layout(view.visualRect(index), view.font(), index)
        if _day_key(index.data(DAY_HEADER_DATE_ROLE)) and chrome.button_rect.contains(pos):
            self._set_button_hover(view, index)
        else:
            self._set_button_hover(view, QModelIndex())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize delegate and enable macros-button hover tracking on the food log view.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._hover_index = QPersistentModelIndex()
        if isinstance(parent, QTableView):
            parent.viewport().setMouseTracking(True)
            parent.viewport().installEventFilter(self)
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Emit `macros_requested` when the day-header macros chip is clicked.

<details>
<summary>Code:</summary>

```python
def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if not bool(index.data(IS_DAY_HEADER_ROLE)):
            return super().editorEvent(event, model, option, index)
        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            day = _day_key(index.data(DAY_HEADER_DATE_ROLE))
            layout = _day_header_chrome_layout(option.rect, option.font, index)
            if day and layout.button_rect.contains(event.position().toPoint()):
                self.macros_requested.emit(day)
                return True
        return super().editorEvent(event, model, option, index)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Track pointer hover over the day-header macros button.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        view = self.parent()
        if isinstance(view, QTableView) and watched is view.viewport():
            self._update_hover(view, event)
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw day/month header chrome, or fall through for ordinary cells.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        is_day = bool(index.data(IS_DAY_HEADER_ROLE))
        is_month = bool(index.data(IS_MONTH_HEADER_ROLE))
        if not is_day and not is_month:
            super().paint(painter, option, index)
            return

        date_text = str(index.data(DAY_HEADER_DATE_ROLE) or "")
        host = option.widget if isinstance(option.widget, QWidget) else None
        fluent = palette_for(host)
        fill = index.data(Qt.ItemDataRole.BackgroundRole)
        # Month banners follow the painting host — avoid palette_for(None) light fills.
        if is_month:
            background = _month_header_fill(fluent)
        elif isinstance(fill, QColor):
            background = fill
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

        chrome = _day_header_chrome_layout(option.rect, option.font, index)
        date_width = max(0, text_rect.width() - chrome.right_block_width - 12)

        painter.setFont(date_font)
        painter.setPen(muted)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            date_metrics.elidedText(date_text, Qt.TextElideMode.ElideRight, date_width),
        )

        if chrome.summary_text and chrome.summary_rect.width() > 0:
            painter.setFont(metrics_font)
            painter.setPen(ink)
            painter.drawText(
                chrome.summary_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                QFontMetrics(metrics_font).elidedText(
                    chrome.summary_text,
                    Qt.TextElideMode.ElideRight,
                    chrome.summary_rect.width(),
                ),
            )

        if chrome.chip_rect is not None:
            chip_color = _threshold_color(index.data(DAY_HEADER_THRESHOLD_RGB_ROLE))
            if chip_color is not None:
                painter.save()
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(chip_color)
                painter.drawRoundedRect(chrome.chip_rect, _CHIP_RADIUS, _CHIP_RADIUS)
                painter.restore()

        if chrome.button_rect.width() >= _MIN_BUTTON_SIZE:
            status = _macros_status_from_role(index.data(DAY_HEADER_MACROS_STATUS_ROLE))
            appearance = macros_button_appearance(status)
            button_font = QFont(option.font)
            button_font.setBold(False)
            self._paint_macros_button(
                painter,
                chrome.button_rect,
                appearance,
                button_font,
                hovered=self._hover_index.isValid() and self._hover_index == index,
            )

        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Make month banners slightly taller than day headers.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        hint = super().sizeHint(option, index)
        min_height = hint.height()
        if bool(index.data(IS_MONTH_HEADER_ROLE)):
            min_height = max(min_height, _MONTH_MIN_HEIGHT)
        elif bool(index.data(IS_DAY_HEADER_ROLE)):
            min_height = max(min_height, _BUTTON_HEIGHT + 8)
        return QSize(hint.width(), min_height)
```

</details>

## 🏛️ Class `FoodDayHeaderProxy`

```python
class FoodDayHeaderProxy(QAbstractProxyModel)
```

Proxy that inserts day and month header rows into the food log list.

<details>
<summary>Code:</summary>

```python
class FoodDayHeaderProxy(QAbstractProxyModel):

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
                    return _month_header_fill(FluentTheme.instance().palette())
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
                    return _month_header_fill(FluentTheme.instance().palette())
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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Create an empty day-header proxy.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
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
```

</details>

### ⚙️ Method `columnCount`

```python
def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int
```

Match the source column count.

<details>
<summary>Code:</summary>

```python
def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:  # noqa: N802
        if parent is not None and parent.isValid():
            return 0
        source = self.sourceModel()
        return 0 if source is None else source.columnCount()
```

</details>

### ⚙️ Method `data`

```python
def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any
```

Return header metadata or forward to the source model.

<details>
<summary>Code:</summary>

```python
def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
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
                    return _month_header_fill(FluentTheme.instance().palette())
                return day_band_color(self._header_bands.get(proxy_row, 0))
            return None
        source_index = self.mapToSource(index)
        if not source_index.isValid():
            return None
        source = self.sourceModel()
        return None if source is None else source.data(source_index, role)
```

</details>

### ⚙️ Method `flags`

```python
def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag
```

Headers are enabled only (not selectable or editable).

<details>
<summary>Code:</summary>

```python
def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if self._is_header_row(index.row()):
            return Qt.ItemFlag.ItemIsEnabled
        source_index = self.mapToSource(index)
        source = self.sourceModel()
        if source is None or not source_index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return source.flags(source_index)
```

</details>

### ⚙️ Method `headerData`

```python
def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any
```

Forward horizontal headers; leave vertical IDs empty on day/month headers.

<details>
<summary>Code:</summary>

```python
def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
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
                return day_band_color(self._header_bands.get(section, 0))
            return None
        return source.headerData(self._proxy_rows[section], orientation, role)
```

</details>

### ⚙️ Method `index`

```python
def index(self, row: int, column: int, parent: QModelIndex | QPersistentModelIndex | None = None) -> QModelIndex
```

Create a proxy index for a mapped row.

<details>
<summary>Code:</summary>

```python
def index(
        self,
        row: int,
        column: int,
        parent: QModelIndex | QPersistentModelIndex | None = None,
    ) -> QModelIndex:
        if parent is not None and parent.isValid():
            return QModelIndex()
        if row < 0 or column < 0 or row >= len(self._proxy_rows) or column >= self.columnCount():
            return QModelIndex()
        return self.createIndex(row, column)
```

</details>

### ⚙️ Method `mapFromSource`

```python
def mapFromSource(self, source_index: QModelIndex | QPersistentModelIndex) -> QModelIndex
```

Map a source index to the corresponding proxy data row.

<details>
<summary>Code:</summary>

```python
def mapFromSource(self, source_index: QModelIndex | QPersistentModelIndex) -> QModelIndex:  # noqa: N802
        if not source_index.isValid():
            return QModelIndex()
        proxy_row = self._source_to_proxy.get(source_index.row())
        if proxy_row is None:
            return QModelIndex()
        return self.index(proxy_row, source_index.column())
```

</details>

### ⚙️ Method `mapToSource`

```python
def mapToSource(self, proxy_index: QModelIndex | QPersistentModelIndex) -> QModelIndex
```

Map a proxy data row to the source; headers map to an invalid index.

<details>
<summary>Code:</summary>

```python
def mapToSource(self, proxy_index: QModelIndex | QPersistentModelIndex) -> QModelIndex:  # noqa: N802
        if not proxy_index.isValid() or self._is_header_row(proxy_index.row()):
            return QModelIndex()
        source = self.sourceModel()
        if source is None:
            return QModelIndex()
        return source.index(self._proxy_rows[proxy_index.row()], proxy_index.column())
```

</details>

### ⚙️ Method `parent (overload)`

```python
def parent(self, /) -> QObject | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def parent(self, /) -> QObject | None: ...
```

</details>

### ⚙️ Method `parent (overload 2)`

```python
def parent(self, child: QModelIndex | QPersistentModelIndex, /) -> QModelIndex
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def parent(self, child: QModelIndex | QPersistentModelIndex, /) -> QModelIndex: ...
```

</details>

### ⚙️ Method `parent`

```python
def parent(self, child: QModelIndex | QPersistentModelIndex | None = None, /) -> QModelIndex | QObject | None
```

QObject parent, or an invalid model parent for this flat table.

<details>
<summary>Code:</summary>

```python
def parent(
        self,
        child: QModelIndex | QPersistentModelIndex | None = None,
        /,
    ) -> QModelIndex | QObject | None:
        if child is None:
            return QObject.parent(self)
        return QModelIndex()
```

</details>

### ⚙️ Method `rebuild`

```python
def rebuild(self) -> None
```

Rebuild header insertion from the current source row order.

<details>
<summary>Code:</summary>

```python
def rebuild(self) -> None:
        self._rebuild_mapping()
```

</details>

### ⚙️ Method `rowCount`

```python
def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int
```

Return data rows plus inserted day/month headers.

<details>
<summary>Code:</summary>

```python
def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:  # noqa: N802
        if parent is not None and parent.isValid():
            return 0
        return len(self._proxy_rows)
```

</details>

### ⚙️ Method `setSourceModel`

```python
def setSourceModel(self, source_model: QAbstractItemModel | None) -> None
```

Attach `source_model` and rebuild the day-header mapping.

<details>
<summary>Code:</summary>

```python
def setSourceModel(self, source_model: QAbstractItemModel | None) -> None:  # noqa: N802
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
```

</details>

### ⚙️ Method `set_calorie_thresholds`

```python
def set_calorie_thresholds(self, thresholds: CalorieThresholds) -> None
```

Replace configured kcal bands used for header threshold chips.

<details>
<summary>Code:</summary>

```python
def set_calorie_thresholds(self, thresholds: CalorieThresholds) -> None:
        self._calorie_thresholds = thresholds
        self._refresh_day_header_metadata()
```

</details>

### ⚙️ Method `set_macros_statuses`

```python
def set_macros_statuses(self, statuses: dict[str, DayMacrosStatus]) -> None
```

Replace cached day-macros button states for header rows.

<details>
<summary>Code:</summary>

```python
def set_macros_statuses(self, statuses: dict[str, DayMacrosStatus]) -> None:
        self._macros_statuses = dict(statuses)
        self._refresh_day_header_metadata()
```

</details>

### ⚙️ Method `sort`

```python
def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None
```

Sort the inner model, then rebuild day headers for the new order.

<details>
<summary>Code:</summary>

```python
def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        source = self.sourceModel()
        if source is None:
            return
        source.sort(column, order)
        self._rebuild_mapping()
```

</details>

## 🔧 Function `apply_food_day_header_spans`

```python
def apply_food_day_header_spans(view: QTableView) -> None
```

Span each day/month header row across all columns.

<details>
<summary>Code:</summary>

```python
def apply_food_day_header_spans(view: QTableView) -> None:
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
```

</details>

## 🔧 Function `food_day_header_delegate_for_view`

```python
def food_day_header_delegate_for_view(view: QTableView) -> FoodDayHeaderDelegate | None
```

Return the day-header delegate installed on column 0, if any.

<details>
<summary>Code:</summary>

```python
def food_day_header_delegate_for_view(view: QTableView) -> FoodDayHeaderDelegate | None:
    delegate = view.itemDelegateForColumn(0)
    if isinstance(delegate, FoodDayHeaderDelegate):
        return delegate
    if isinstance(delegate, _FoodDayHeaderOrDelegate):
        return delegate.food_day_header_delegate
    return None
```

</details>

## 🔧 Function `install_food_day_headers`

```python
def install_food_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> FoodDayHeaderProxy
```

Wrap `sort_proxy` with day/month headers and show it on `view`.

<details>
<summary>Code:</summary>

```python
def install_food_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> FoodDayHeaderProxy:
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
```

</details>

## 🔧 Function `is_food_day_or_month_header`

```python
def is_food_day_or_month_header(index: QModelIndex) -> bool
```

Return whether `index` is a food log day or month group header row.

<details>
<summary>Code:</summary>

```python
def is_food_day_or_month_header(index: QModelIndex) -> bool:
    if not index.isValid():
        return False
    return bool(index.data(IS_DAY_HEADER_ROLE)) or bool(index.data(IS_MONTH_HEADER_ROLE))
```

</details>

## 🔧 Function `map_food_log_index_to_source`

```python
def map_food_log_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]
```

Walk proxy layers until the ultimate source model index.

<details>
<summary>Code:</summary>

```python
def map_food_log_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]:
    model: Any = index.model()
    current = index
    while isinstance(model, QAbstractProxyModel):
        current = model.mapToSource(current)
        if not current.isValid():
            return current, model.sourceModel()
        model = model.sourceModel()
    return current, model
```

</details>

## 🔧 Function `ultimate_food_log_source`

```python
def ultimate_food_log_source(model: Any) -> Any
```

Return the innermost model under nested proxies.

<details>
<summary>Code:</summary>

```python
def ultimate_food_log_source(model: Any) -> Any:
    current = model
    while isinstance(current, QAbstractProxyModel):
        current = current.sourceModel()
    return current
```

</details>
