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
- [🔧 Function `readable_cell_fill`](#-function-readable_cell_fill)
- [🔧 Function `readable_row_tint`](#-function-readable_row_tint)
- [🔧 Function `refresh_day_bands`](#-function-refresh_day_bands)
- [🔧 Function `set_day_band`](#-function-set_day_band)
- [🔧 Function `set_readable_cell_fill`](#-function-set_readable_cell_fill)
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
        # Fluent ink — do not trust ButtonText (stays light-theme dark under dark bands).
        painter.setPen(self._section_ink(logical_index))
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

    def _section_ink(self, logical_index: int) -> QColor:
        """Return on-theme ID text, preferring the row's stored day-band foreground."""
        model = self.model()
        if model is not None:
            brush = model.headerData(logical_index, Qt.Orientation.Vertical, Qt.ItemDataRole.ForegroundRole)
            if isinstance(brush, QBrush) and brush.style() != Qt.BrushStyle.NoBrush:
                return brush.color()
            if isinstance(brush, QColor) and brush.isValid():
                return brush
        return _band_ink()
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
        # Fluent ink — do not trust ButtonText (stays light-theme dark under dark bands).
        painter.setPen(self._section_ink(logical_index))
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
def install_day_band_vertical_header(table: QTableView) -> QHeaderView
```

Use a day-band ID header on `table`, keeping the one already installed.

Preserves row heights from the previous header. Replacing the header without
copying `defaultSectionSize` used to shrink thumbnail tables (Workouts) so
64px icons overlapped across ~30px rows.

Hidden vertical headers (no record-id column) are left alone.

<details>
<summary>Code:</summary>

```python
def install_day_band_vertical_header(table: QTableView) -> QHeaderView:
    current = table.verticalHeader()
    if isinstance(current, DayBandVerticalHeader):
        return current
    if current.isHidden():
        return current
    default_size = current.defaultSectionSize()
    min_size = current.minimumSectionSize()
    section_sizes = [current.sectionSize(index) for index in range(current.count())]
    header = DayBandVerticalHeader(table)
    header.setVisible(True)
    header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
    header.setMinimumWidth(current.minimumWidth())
    header.setMinimumSectionSize(min_size)
    header.setDefaultSectionSize(default_size)
    table.setVerticalHeader(header)
    # setVerticalHeader can reset metrics; restore after the swap.
    header.setMinimumSectionSize(min_size)
    header.setDefaultSectionSize(default_size)
    for index, size in enumerate(section_sizes):
        header.resizeSection(index, size)
    return header
```

</details>

## 🔧 Function `readable_cell_fill`

```python
def readable_cell_fill(light: QColor, *, band_index: int = 0) -> QColor
```

Return a cell fill that stays readable with Fluent text in dark theme.

Light mode keeps `light`. Dark mode darkens chromatic pastels (hue kept) so
light table text remains legible, and maps near-gray pastels to the neutral
day band.

<details>
<summary>Code:</summary>

```python
def readable_cell_fill(light: QColor, *, band_index: int = 0) -> QColor:
    if not FluentTheme.instance().palette().dark:
        return QColor(light)
    hue = light.hue()
    saturation = light.saturation()
    value = light.value()
    alpha = light.alpha()
    if hue < 0 or saturation < _MIN_CHROMATIC_SATURATION:
        return day_band_color(band_index % 2)
    dark_value = min(100, max(48, value // 3))
    dark_saturation = min(255, max(saturation, 90))
    return QColor.fromHsv(hue, dark_saturation, dark_value, alpha)
```

</details>

## 🔧 Function `readable_row_tint`

```python
def readable_row_tint(light: QColor, *, band_index: int = 0) -> DayBand
```

Return a row fill that stays readable in the active Fluent theme.

Light mode keeps the pastel `light` color (tagged so theme refresh works).
Dark mode uses the neutral day band — pastel cells with light text are
illegible on Fluent dark chrome.

<details>
<summary>Code:</summary>

```python
def readable_row_tint(light: QColor, *, band_index: int = 0) -> DayBand:
    index = band_index % 2
    if FluentTheme.instance().palette().dark:
        return day_band_color(index)
    return DayBand(light.red(), light.green(), light.blue(), index)
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

Plain pastel `QColor` values (not [`DayBand`](#%EF%B8%8F-class-dayband)) go through [`readable_cell_fill`](#-function-readable_cell_fill)
so tracker tables stay legible under Fluent dark chrome.

<details>
<summary>Code:</summary>

```python
def set_day_band(item: QStandardItem, color: QColor) -> None:
    if not isinstance(color, DayBand):
        set_readable_cell_fill(item, color)
        return
    item.setBackground(QBrush(color))
    item.setData(color.band_index, DAY_BAND_ROLE)
    item.setForeground(QBrush(_band_ink()))
```

</details>

## 🔧 Function `set_readable_cell_fill`

```python
def set_readable_cell_fill(item: QStandardItem, light: QColor, *, band_index: int = 0) -> None
```

Paint [`item`](../../fluent/widgets/navigation.g.md#%EF%B8%8F-method-item) with [`readable_cell_fill`](#-function-readable_cell_fill), tagging day bands when used.

<details>
<summary>Code:</summary>

```python
def set_readable_cell_fill(item: QStandardItem, light: QColor, *, band_index: int = 0) -> None:
    fill = readable_cell_fill(light, band_index=band_index)
    if isinstance(fill, DayBand):
        set_day_band(item, fill)
        return
    clear_day_band(item)
    item.setBackground(QBrush(fill))
    item.setForeground(QBrush(_band_ink()))
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
