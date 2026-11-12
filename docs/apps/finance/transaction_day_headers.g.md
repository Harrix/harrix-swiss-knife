---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transaction_day_headers.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DayHeaderDelegate`](#%EF%B8%8F-class-dayheaderdelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
- [🏛️ Class `TransactionDayHeaderProxy`](#%EF%B8%8F-class-transactiondayheaderproxy)
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
- [🔧 Function `apply_transaction_day_header_spans`](#-function-apply_transaction_day_header_spans)
- [🔧 Function `install_transaction_day_headers`](#-function-install_transaction_day_headers)
- [🔧 Function `map_transactions_index_to_source`](#-function-map_transactions_index_to_source)
- [🔧 Function `ultimate_transactions_source`](#-function-ultimate_transactions_source)

</details>

## 🏛️ Class `DayHeaderDelegate`

```python
class DayHeaderDelegate(QStyledItemDelegate)
```

Paint a compact day header (date left, day total above Amount) for spanned rows.

<details>
<summary>Code:</summary>

```python
class DayHeaderDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the day header chrome, or fall through for ordinary cells."""
        if not bool(index.data(IS_DAY_HEADER_ROLE)):
            super().paint(painter, option, index)
            return

        date_text = str(index.data(DAY_HEADER_DATE_ROLE) or "")
        total_raw = str(index.data(DAY_HEADER_TOTAL_ROLE) or "")
        host = option.widget if isinstance(option.widget, QWidget) else None
        fluent = palette_for(host)
        fill = index.data(Qt.ItemDataRole.BackgroundRole)
        background = fill if isinstance(fill, QColor) else mix(fluent.window_bg, fluent.card_bg)
        ink = mix(fluent.window_bg, fluent.text_primary)
        muted = mix(fluent.window_bg, fluent.text_secondary)
        hairline = mix(fluent.window_bg, fluent.divider)
        hairline.setAlpha(_SEPARATOR_ALPHA)

        painter.save()
        painter.fillRect(option.rect, background)
        if index.row() > 0:
            painter.setPen(QPen(hairline, 1))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())

        font = QFont(option.font)
        font.setBold(True)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        # Align the day total with the Amount column so it does not sit over Tag.
        total_right = _day_header_total_right(host, option.rect)
        text_left = option.rect.left() + _HEADER_PAD_X
        text_right = max(text_left, total_right - _HEADER_PAD_X)
        text_rect = QRect(text_left, option.rect.top(), text_right - text_left, option.rect.height())

        total_display = _format_header_total(total_raw, host)
        total_width = metrics.horizontalAdvance(total_display) if total_display else 0
        date_width = max(0, text_rect.width() - total_width - 12)
        painter.setPen(ink)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            metrics.elidedText(date_text, Qt.TextElideMode.ElideRight, date_width),
        )
        if total_display:
            painter.setPen(muted if total_display.startswith("-") else ink)
            painter.drawText(
                text_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                total_display,
            )
        painter.restore()
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw the day header chrome, or fall through for ordinary cells.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if not bool(index.data(IS_DAY_HEADER_ROLE)):
            super().paint(painter, option, index)
            return

        date_text = str(index.data(DAY_HEADER_DATE_ROLE) or "")
        total_raw = str(index.data(DAY_HEADER_TOTAL_ROLE) or "")
        host = option.widget if isinstance(option.widget, QWidget) else None
        fluent = palette_for(host)
        fill = index.data(Qt.ItemDataRole.BackgroundRole)
        background = fill if isinstance(fill, QColor) else mix(fluent.window_bg, fluent.card_bg)
        ink = mix(fluent.window_bg, fluent.text_primary)
        muted = mix(fluent.window_bg, fluent.text_secondary)
        hairline = mix(fluent.window_bg, fluent.divider)
        hairline.setAlpha(_SEPARATOR_ALPHA)

        painter.save()
        painter.fillRect(option.rect, background)
        if index.row() > 0:
            painter.setPen(QPen(hairline, 1))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())

        font = QFont(option.font)
        font.setBold(True)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        # Align the day total with the Amount column so it does not sit over Tag.
        total_right = _day_header_total_right(host, option.rect)
        text_left = option.rect.left() + _HEADER_PAD_X
        text_right = max(text_left, total_right - _HEADER_PAD_X)
        text_rect = QRect(text_left, option.rect.top(), text_right - text_left, option.rect.height())

        total_display = _format_header_total(total_raw, host)
        total_width = metrics.horizontalAdvance(total_display) if total_display else 0
        date_width = max(0, text_rect.width() - total_width - 12)
        painter.setPen(ink)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            metrics.elidedText(date_text, Qt.TextElideMode.ElideRight, date_width),
        )
        if total_display:
            painter.setPen(muted if total_display.startswith("-") else ink)
            painter.drawText(
                text_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight),
                total_display,
            )
        painter.restore()
```

</details>

## 🏛️ Class `TransactionDayHeaderProxy`

```python
class TransactionDayHeaderProxy(QAbstractProxyModel)
```

Proxy that inserts a day header row before each consecutive date group.

<details>
<summary>Code:</summary>

```python
class TransactionDayHeaderProxy(QAbstractProxyModel):

    mapping_reset = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        """Create an empty day-header proxy."""
        super().__init__(parent)
        self._proxy_rows: list[int] = []  # source row, or -1 for a header
        self._header_dates: dict[int, str] = {}
        self._header_totals: dict[int, str] = {}
        self._header_bands: dict[int, int] = {}
        self._source_to_proxy: dict[int, int] = {}

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
            if role == IS_DAY_HEADER_ROLE:
                return True
            if role == DAY_HEADER_DATE_ROLE:
                return self._header_dates.get(proxy_row, "")
            if role == DAY_HEADER_TOTAL_ROLE:
                return self._header_totals.get(proxy_row, "")
            if role == Qt.ItemDataRole.DisplayRole:
                if index.column() == 0:
                    return self._header_dates.get(proxy_row, "")
                if index.column() == TRANSACTION_COL_TOTAL_PER_DAY:
                    return self._header_totals.get(proxy_row, "")
                return ""
            if role == Qt.ItemDataRole.BackgroundRole:
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
        """Forward horizontal headers; leave vertical IDs empty on day headers."""
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
        self.mapping_reset.emit()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:  # noqa: N802
        """Return data rows plus inserted day headers."""
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

    def _band_index_for_header(self, proxy_row: int) -> int:
        return self._header_bands.get(proxy_row, 0)

    def _is_header_row(self, proxy_row: int) -> bool:
        return 0 <= proxy_row < len(self._proxy_rows) and self._proxy_rows[proxy_row] < 0

    def _on_source_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        _roles: list[int] | None = None,
    ) -> None:
        if top_left.column() <= TRANSACTION_COL_DATE <= bottom_right.column() or (
            top_left.column() <= TRANSACTION_COL_TOTAL_PER_DAY <= bottom_right.column()
        ):
            self._rebuild_mapping()
            return
        for source_row in range(top_left.row(), bottom_right.row() + 1):
            proxy_row = self._source_to_proxy.get(source_row)
            if proxy_row is None:
                continue
            left = self.index(proxy_row, top_left.column())
            right = self.index(proxy_row, bottom_right.column())
            self.dataChanged.emit(left, right)

    def _on_source_reset(self, *_args: object) -> None:
        self._rebuild_mapping()

    def _rebuild_mapping(self) -> None:
        self.beginResetModel()
        self._proxy_rows = []
        self._header_dates = {}
        self._header_totals = {}
        self._header_bands = {}
        self._source_to_proxy = {}
        source = self.sourceModel()
        if source is None:
            self.endResetModel()
            self.mapping_reset.emit()
            return

        previous_date = object()
        band_index = 0
        for source_row in range(source.rowCount()):
            date_value = source.index(source_row, TRANSACTION_COL_DATE).data(Qt.ItemDataRole.DisplayRole)
            date_str = "" if date_value is None else str(date_value)
            if date_str and date_str != previous_date:
                total_value = source.index(source_row, TRANSACTION_COL_TOTAL_PER_DAY).data(Qt.ItemDataRole.DisplayRole)
                total_text = "" if total_value is None else str(total_value)
                header_row = len(self._proxy_rows)
                self._proxy_rows.append(-1)
                self._header_dates[header_row] = date_str
                self._header_totals[header_row] = total_text
                self._header_bands[header_row] = band_index
                band_index = 1 - band_index
                previous_date = date_str
            self._source_to_proxy[source_row] = len(self._proxy_rows)
            self._proxy_rows.append(source_row)
        self.endResetModel()
        self.mapping_reset.emit()
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
        self._proxy_rows: list[int] = []  # source row, or -1 for a header
        self._header_dates: dict[int, str] = {}
        self._header_totals: dict[int, str] = {}
        self._header_bands: dict[int, int] = {}
        self._source_to_proxy: dict[int, int] = {}
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
            if role == IS_DAY_HEADER_ROLE:
                return True
            if role == DAY_HEADER_DATE_ROLE:
                return self._header_dates.get(proxy_row, "")
            if role == DAY_HEADER_TOTAL_ROLE:
                return self._header_totals.get(proxy_row, "")
            if role == Qt.ItemDataRole.DisplayRole:
                if index.column() == 0:
                    return self._header_dates.get(proxy_row, "")
                if index.column() == TRANSACTION_COL_TOTAL_PER_DAY:
                    return self._header_totals.get(proxy_row, "")
                return ""
            if role == Qt.ItemDataRole.BackgroundRole:
                return day_band_color(self._band_index_for_header(proxy_row))
            if role in {Qt.ItemDataRole.FontRole, Qt.ItemDataRole.TextAlignmentRole}:
                return None
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

Forward horizontal headers; leave vertical IDs empty on day headers.

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
                return day_band_color(self._band_index_for_header(section))
            return None
        source_row = self._proxy_rows[section]
        return source.headerData(source_row, orientation, role)
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
        source_row = self._proxy_rows[proxy_index.row()]
        return source.index(source_row, proxy_index.column())
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
        self.mapping_reset.emit()
```

</details>

### ⚙️ Method `rowCount`

```python
def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int
```

Return data rows plus inserted day headers.

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

## 🔧 Function `apply_transaction_day_header_spans`

```python
def apply_transaction_day_header_spans(view: QTableView) -> None
```

Span each day-header row across all columns so one cell paints the banner.

<details>
<summary>Code:</summary>

```python
def apply_transaction_day_header_spans(view: QTableView) -> None:
    model = view.model()
    view.clearSpans()
    if model is None:
        return
    columns = model.columnCount()
    if columns <= 0:
        return
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if bool(model.data(index, IS_DAY_HEADER_ROLE)):
            view.setSpan(row, 0, 1, columns)
```

</details>

## 🔧 Function `install_transaction_day_headers`

```python
def install_transaction_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> TransactionDayHeaderProxy
```

Wrap `sort_proxy` with day headers and show it on `view`.

<details>
<summary>Code:</summary>

```python
def install_transaction_day_headers(view: QTableView, sort_proxy: QAbstractItemModel) -> TransactionDayHeaderProxy:
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
```

</details>

## 🔧 Function `map_transactions_index_to_source`

```python
def map_transactions_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]
```

Walk proxy layers until the ultimate source model index.

<details>
<summary>Code:</summary>

```python
def map_transactions_index_to_source(index: QModelIndex) -> tuple[QModelIndex, Any]:
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

## 🔧 Function `ultimate_transactions_source`

```python
def ultimate_transactions_source(model: Any) -> Any
```

Return the innermost model under nested proxies.

<details>
<summary>Code:</summary>

```python
def ultimate_transactions_source(model: Any) -> Any:
    current = model
    while isinstance(current, QAbstractProxyModel):
        current = current.sourceModel()
    return current
```

</details>
