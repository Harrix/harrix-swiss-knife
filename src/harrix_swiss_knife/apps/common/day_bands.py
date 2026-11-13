"""Theme-aware day bands for tracker tables.

Consecutive days alternate two neutral fills from the current Fluent palette.
The same fill is stored on the row and on the record-id header so the day
reads across the whole row, including the ID column.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QAbstractProxyModel, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPalette, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QHeaderView, QTableView

from harrix_swiss_knife.fluent.theme import FluentTheme, mix

if TYPE_CHECKING:
    from PySide6.QtCore import QRect

    from harrix_swiss_knife.fluent.tokens import FluentPalette

DAY_BAND_ROLE = Qt.ItemDataRole.UserRole + 410
_MIN_CHROMATIC_SATURATION = 25


class DayBand(QColor):
    """One neutral day fill, tagged with its band index (0 or 1)."""

    def __init__(self, red: int, green: int, blue: int, band_index: int) -> None:
        """Create an opaque band color for `band_index`."""
        super().__init__(red, green, blue)
        self.band_index = band_index


class DayBandVerticalHeader(QHeaderView):
    """Record-id header that paints each section with that row's day band."""

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


def clear_day_band(item: QStandardItem) -> None:
    """Drop a day-band mark so a later semantic color is left in place."""
    item.setData(None, DAY_BAND_ROLE)


def day_band_color(index: int) -> DayBand:
    """Return the neutral fill for day `index` in the current theme."""
    return day_band_colors()[index % 2]


def day_band_colors() -> list[DayBand]:
    """Return the even and odd day fills for the current theme."""
    even, odd = _band_pair(FluentTheme.instance().palette())
    return [DayBand(*even, 0), DayBand(*odd, 1)]


def day_band_id_item(row_id: object, color: QColor) -> QStandardItem:
    """Build a vertical-header ID cell, tinted when `color` is a day band."""
    item = QStandardItem("" if row_id is None else str(row_id))
    if isinstance(color, DayBand):
        set_day_band(item, color)
    return item


def install_day_band_vertical_header(table: QTableView) -> QHeaderView:
    """Use a day-band ID header on `table`, keeping the one already installed.

    Preserves row heights from the previous header. Replacing the header without
    copying `defaultSectionSize` used to shrink thumbnail tables (Workouts) so
    64px icons overlapped across ~30px rows.

    Hidden vertical headers (no record-id column) are left alone.

    """
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


def readable_cell_fill(light: QColor, *, band_index: int = 0) -> QColor:
    """Return a cell fill that stays readable with Fluent text in dark theme.

    Light mode keeps `light`. Dark mode darkens chromatic pastels (hue kept) so
    light table text remains legible, and maps near-gray pastels to the neutral
    day band.

    """
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


def readable_row_tint(light: QColor, *, band_index: int = 0) -> DayBand:
    """Return a row fill that stays readable in the active Fluent theme.

    Light mode keeps the pastel `light` color (tagged so theme refresh works).
    Dark mode uses the neutral day band — pastel cells with light text are
    illegible on Fluent dark chrome.

    """
    index = band_index % 2
    if FluentTheme.instance().palette().dark:
        return day_band_color(index)
    return DayBand(light.red(), light.green(), light.blue(), index)


def refresh_day_bands(table: QTableView) -> None:
    """Repaint stored day bands with the colors of the current theme."""
    model = table.model()
    while isinstance(model, QAbstractProxyModel):
        model = model.sourceModel()
    if not isinstance(model, QStandardItemModel):
        return
    _refresh_model(model)


def set_day_band(item: QStandardItem, color: QColor) -> None:
    """Paint `item` with `color` and remember the band index when it has one.

    Plain pastel `QColor` values (not `DayBand`) go through `readable_cell_fill`
    so tracker tables stay legible under Fluent dark chrome.

    """
    if not isinstance(color, DayBand):
        set_readable_cell_fill(item, color)
        return
    item.setBackground(QBrush(color))
    item.setData(color.band_index, DAY_BAND_ROLE)
    item.setForeground(QBrush(_band_ink()))


def set_readable_cell_fill(item: QStandardItem, light: QColor, *, band_index: int = 0) -> None:
    """Paint `item` with `readable_cell_fill`, tagging day bands when used."""
    fill = readable_cell_fill(light, band_index=band_index)
    if isinstance(fill, DayBand):
        set_day_band(item, fill)
        return
    clear_day_band(item)
    item.setBackground(QBrush(fill))
    item.setForeground(QBrush(_band_ink()))


def table_surface_color(palette: FluentPalette) -> QColor:
    """Return the table and column-header fill for `palette` (the even day band)."""
    red, green, blue = _band_pair(palette)[0]
    return QColor(red, green, blue)


def _band_ink() -> QColor:
    """Return primary text color readable on the current day-band fills."""
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.text_primary)


def _band_pair(palette: FluentPalette) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Return even and odd RGB triples. Odd is darker in light mode and lighter in dark.

    Bands stay cool-neutral (not rainbow pastels) with a clear step between days,
    while staying lighter than soft-blue selection chrome (`#eaf1f8`).

    """
    if palette.dark:
        return (0x2A, 0x2A, 0x2C), (0x3A, 0x3D, 0x42)
    return (0xFC, 0xFC, 0xFC), (0xE4, 0xE8, 0xED)


def _refresh_model(model: QStandardItemModel) -> None:
    """Repaint day-band fills without emitting per-cell `dataChanged` storms."""
    rows = model.rowCount()
    columns = model.columnCount()
    if rows <= 0 or columns <= 0:
        return
    ink = QBrush(_band_ink())
    model.blockSignals(True)  # noqa: FBT003
    try:
        for row in range(rows):
            band: int | None = None
            for column in range(columns):
                item = model.item(row, column)
                if item is None:
                    continue
                stored = item.data(DAY_BAND_ROLE)
                if not isinstance(stored, int):
                    continue
                band = stored
                item.setBackground(QBrush(day_band_color(stored)))
                item.setForeground(ink)
            header = model.verticalHeaderItem(row)
            if header is not None and band is not None:
                set_day_band(header, day_band_color(band))
    finally:
        model.blockSignals(False)  # noqa: FBT003
    top_left = model.index(0, 0)
    bottom_right = model.index(rows - 1, columns - 1)
    model.dataChanged.emit(
        top_left,
        bottom_right,
        [int(Qt.ItemDataRole.BackgroundRole), int(Qt.ItemDataRole.ForegroundRole)],
    )
