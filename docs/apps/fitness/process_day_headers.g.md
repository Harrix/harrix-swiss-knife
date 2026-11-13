---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `process_day_headers.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ProcessDayHeaderDelegate`](#%EF%B8%8F-class-processdayheaderdelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🏛️ Class `ProcessDayHeaderProxy`](#%EF%B8%8F-class-processdayheaderproxy)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
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
  - [⚙️ Method `sort`](#%EF%B8%8F-method-sort)
- [🔧 Function `apply_process_day_header_spans`](#-function-apply_process_day_header_spans)
- [🔧 Function `install_process_day_headers`](#-function-install_process_day_headers)
- [🔧 Function `map_process_index_to_source`](#-function-map_process_index_to_source)
- [🔧 Function `ultimate_process_source`](#-function-ultimate_process_source)

</details>

## 🏛️ Class `ProcessDayHeaderDelegate`

```python
class ProcessDayHeaderDelegate(QStyledItemDelegate)
```

Paint day/month headers (label left, Sets count right) for spanned rows.

<details>
<summary>Code:</summary>

```python
class ProcessDayHeaderDelegate(QStyledItemDelegate):

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
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw the day/month header chrome, or fall through for ordinary cells.

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
        if bool(index.data(IS_MONTH_HEADER_ROLE)):
            return QSize(hint.width(), max(hint.height(), _MONTH_MIN_HEIGHT))
        return hint
```

</details>

## 🏛️ Class `ProcessDayHeaderProxy`

```python
class ProcessDayHeaderProxy(QAbstractProxyModel)
```

Proxy that inserts day and month header rows into the process list.

<details>
<summary>Code:</summary>

```python
class ProcessDayHeaderProxy(QAbstractProxyModel):

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
        self._header_sets: dict[int, str] = {}
        self._header_bands: dict[int, int] = {}
        self._header_month_rows: set[int] = set()
        self._header_current_month_rows: set[int] = set()
        self._source_to_proxy: dict[int, int] = {}
        self._rebuild_scheduled = False
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
                    return _month_header_fill(palette_for(None))
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

## 🔧 Function `apply_process_day_header_spans`

```python
def apply_process_day_header_spans(view: QTableView) -> None
```

Span each day/month header row across all columns.

<details>
<summary>Code:</summary>

```python
def apply_process_day_header_spans(view: QTableView) -> None:
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

## 🔧 Function `install_process_day_headers`

```python
def install_process_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> ProcessDayHeaderProxy
```

Wrap `sort_proxy` with day/month headers and show it on `view`.

<details>
<summary>Code:</summary>

```python
def install_process_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> ProcessDayHeaderProxy:
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
```

</details>

## 🔧 Function `map_process_index_to_source`

```python
def map_process_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]
```

Walk proxy layers until the ultimate source model index.

<details>
<summary>Code:</summary>

```python
def map_process_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]:
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

## 🔧 Function `ultimate_process_source`

```python
def ultimate_process_source(model: Any) -> Any
```

Return the innermost model under nested proxies.

<details>
<summary>Code:</summary>

```python
def ultimate_process_source(model: Any) -> Any:
    current = model
    while isinstance(current, QAbstractProxyModel):
        current = current.sourceModel()
    return current
```

</details>
