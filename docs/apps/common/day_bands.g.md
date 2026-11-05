---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `day_bands.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DayBand`](#%EF%B8%8F-class-dayband)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🏛️ Class `DayBandVerticalHeader`](#%EF%B8%8F-class-daybandverticalheader)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `paintSection`](#%EF%B8%8F-method-paintsection)
- [🔧 Function `clear_day_band`](#-function-clear_day_band)
- [🔧 Function `day_band_color`](#-function-day_band_color)
- [🔧 Function `day_band_colors`](#-function-day_band_colors)
- [🔧 Function `day_band_id_item`](#-function-day_band_id_item)
- [🔧 Function `install_day_band_vertical_header`](#-function-install_day_band_vertical_header)
- [🔧 Function `refresh_day_bands`](#-function-refresh_day_bands)
- [🔧 Function `set_day_band`](#-function-set_day_band)
- [🔧 Function `table_surface_color`](#-function-table_surface_color)

</details>

## 🏛️ Class `DayBand`

```python
class DayBand(QColor)
```

One neutral day fill, tagged with its band index (0 or 1).

<details>
<summary>Code:</summary>

```python
class DayBand(QColor):

    def __init__(self, red: int, green: int, blue: int, band_index: int) -> None:
        """Create an opaque band color for `band_index`."""
        super().__init__(red, green, blue)
        self.band_index = band_index
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, red: int, green: int, blue: int, band_index: int) -> None
```

Create an opaque band color for `band_index`.

<details>
<summary>Code:</summary>

```python
def __init__(self, red: int, green: int, blue: int, band_index: int) -> None:
        super().__init__(red, green, blue)
        self.band_index = band_index
```

</details>

## 🏛️ Class `DayBandVerticalHeader`

```python
class DayBandVerticalHeader(QHeaderView)
```

Record-id header that paints each section with that row's day band.

<details>
<summary>Code:</summary>

```python
class DayBandVerticalHeader(QHeaderView):

    def __init__(self, parent: QTableView | None = None) -> None:
        """Create a vertical header for `parent`."""
        super().__init__(Qt.Orientation.Vertical, parent)
        self.setHighlightSections(False)

    def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:  # noqa: N802
        """Fill the ID cell with the row band, then draw the ID."""
        painter.save()
        painter.fillRect(rect, self._section_fill(logical_index))
        model = self.model()
        text = ""
        if model is not None:
            value = model.headerData(logical_index, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole)
            text = "" if value is None else str(value)
        painter.setPen(self.palette().color(QPalette.ColorRole.ButtonText))
        painter.setFont(self.font())
        painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        painter.restore()

    def _section_fill(self, logical_index: int) -> QColor:
        model = self.model()
        if model is not None:
            brush = model.headerData(logical_index, Qt.Orientation.Vertical, Qt.ItemDataRole.BackgroundRole)
            if isinstance(brush, QBrush) and brush.style() != Qt.BrushStyle.NoBrush:
                return brush.color()
            if isinstance(brush, QColor):
                return brush
        return self.palette().color(QPalette.ColorRole.Button)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QTableView | None = None) -> None
```

Create a vertical header for `parent`.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(Qt.Orientation.Vertical, parent)
        self.setHighlightSections(False)
```

</details>

### ⚙️ Method `paintSection`

```python
def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None
```

Fill the ID cell with the row band, then draw the ID.

<details>
<summary>Code:</summary>

```python
def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:  # noqa: N802
        painter.save()
        painter.fillRect(rect, self._section_fill(logical_index))
        model = self.model()
        text = ""
        if model is not None:
            value = model.headerData(logical_index, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole)
            text = "" if value is None else str(value)
        painter.setPen(self.palette().color(QPalette.ColorRole.ButtonText))
        painter.setFont(self.font())
        painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        painter.restore()
```

</details>

## 🔧 Function `clear_day_band`

```python
def clear_day_band(item: QStandardItem) -> None
```

Drop a day-band mark so a later semantic color is left in place.

<details>
<summary>Code:</summary>

```python
def clear_day_band(item: QStandardItem) -> None:
    item.setData(None, DAY_BAND_ROLE)
```

</details>

## 🔧 Function `day_band_color`

```python
def day_band_color(index: int) -> DayBand
```

Return the neutral fill for day `index` in the current theme.

<details>
<summary>Code:</summary>

```python
def day_band_color(index: int) -> DayBand:
    return day_band_colors()[index % 2]
```

</details>

## 🔧 Function `day_band_colors`

```python
def day_band_colors() -> list[DayBand]
```

Return the even and odd day fills for the current theme.

<details>
<summary>Code:</summary>

```python
def day_band_colors() -> list[DayBand]:
    even, odd = _band_pair(FluentTheme.instance().palette())
    return [DayBand(*even, 0), DayBand(*odd, 1)]
```

</details>

## 🔧 Function `day_band_id_item`

```python
def day_band_id_item(row_id: object, color: QColor) -> QStandardItem
```

Build a vertical-header ID cell, tinted when [`color`](../../fluent/widgets/dialogs.g.md#%EF%B8%8F-method-color) is a day band.

<details>
<summary>Code:</summary>

```python
def day_band_id_item(row_id: object, color: QColor) -> QStandardItem:
    item = QStandardItem("" if row_id is None else str(row_id))
    if isinstance(color, DayBand):
        set_day_band(item, color)
    return item
```

</details>

## 🔧 Function `install_day_band_vertical_header`

```python
def install_day_band_vertical_header(table: QTableView) -> DayBandVerticalHeader
```

Use a day-band ID header on `table`, keeping the one already installed.

<details>
<summary>Code:</summary>

```python
def install_day_band_vertical_header(table: QTableView) -> DayBandVerticalHeader:
    current = table.verticalHeader()
    if isinstance(current, DayBandVerticalHeader):
        return current
    header = DayBandVerticalHeader(table)
    header.setVisible(not current.isHidden())
    header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
    header.setMinimumWidth(current.minimumWidth())
    table.setVerticalHeader(header)
    return header
```

</details>

## 🔧 Function `refresh_day_bands`

```python
def refresh_day_bands(table: QTableView) -> None
```

Repaint stored day bands with the colors of the current theme.

<details>
<summary>Code:</summary>

```python
def refresh_day_bands(table: QTableView) -> None:
    model = table.model()
    while isinstance(model, QAbstractProxyModel):
        model = model.sourceModel()
    if not isinstance(model, QStandardItemModel):
        return
    _refresh_model(model)
```

</details>

## 🔧 Function `set_day_band`

```python
def set_day_band(item: QStandardItem, color: QColor) -> None
```

Paint [`item`](../../fluent/widgets/navigation.g.md#%EF%B8%8F-method-item) with [`color`](../../fluent/widgets/dialogs.g.md#%EF%B8%8F-method-color) and remember the band index when it has one.

<details>
<summary>Code:</summary>

```python
def set_day_band(item: QStandardItem, color: QColor) -> None:
    item.setBackground(QBrush(color))
    band = getattr(color, "band_index", None)
    if isinstance(band, int):
        item.setData(band, DAY_BAND_ROLE)
```

</details>

## 🔧 Function `table_surface_color`

```python
def table_surface_color(palette: FluentPalette) -> QColor
```

Return the table and column-header fill for [`palette`](../../fluent/theme.g.md#%EF%B8%8F-method-palette) (the even day band).

<details>
<summary>Code:</summary>

```python
def table_surface_color(palette: FluentPalette) -> QColor:
    red, green, blue = _band_pair(palette)[0]
    return QColor(red, green, blue)
```

</details>
