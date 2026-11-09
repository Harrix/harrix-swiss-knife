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

from harrix_swiss_knife.fluent.theme import FluentTheme

if TYPE_CHECKING:
    from PySide6.QtCore import QRect

    from harrix_swiss_knife.fluent.tokens import FluentPalette

DAY_BAND_ROLE = Qt.ItemDataRole.UserRole + 410


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


def install_day_band_vertical_header(table: QTableView) -> DayBandVerticalHeader:
    """Use a day-band ID header on `table`, keeping the one already installed."""
    current = table.verticalHeader()
    if isinstance(current, DayBandVerticalHeader):
        return current
    header = DayBandVerticalHeader(table)
    header.setVisible(not current.isHidden())
    header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
    header.setMinimumWidth(current.minimumWidth())
    table.setVerticalHeader(header)
    return header


def refresh_day_bands(table: QTableView) -> None:
    """Repaint stored day bands with the colors of the current theme."""
    model = table.model()
    while isinstance(model, QAbstractProxyModel):
        model = model.sourceModel()
    if not isinstance(model, QStandardItemModel):
        return
    _refresh_model(model)


def set_day_band(item: QStandardItem, color: QColor) -> None:
    """Paint `item` with `color` and remember the band index when it has one."""
    item.setBackground(QBrush(color))
    band = getattr(color, "band_index", None)
    if isinstance(band, int):
        item.setData(band, DAY_BAND_ROLE)


def table_surface_color(palette: FluentPalette) -> QColor:
    """Return the table and column-header fill for `palette` (the even day band)."""
    red, green, blue = _band_pair(palette)[0]
    return QColor(red, green, blue)


def _band_pair(palette: FluentPalette) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Return even and odd RGB triples. Odd is darker in light mode and lighter in dark.

    Light bands stay near-white with a very weak neutral tint so day groups do not
    look like a multi-row selection over the Fluent wallpaper.

    """
    if palette.dark:
        return (0x2C, 0x2C, 0x2C), (0x36, 0x36, 0x36)
    return (0xFC, 0xFC, 0xFC), (0xF4, 0xF5, 0xF6)


def _refresh_model(model: QStandardItemModel) -> None:
    for row in range(model.rowCount()):
        band: int | None = None
        for column in range(model.columnCount()):
            item = model.item(row, column)
            if item is None:
                continue
            stored = item.data(DAY_BAND_ROLE)
            if not isinstance(stored, int):
                continue
            band = stored
            item.setBackground(QBrush(day_band_color(stored)))
        header = model.verticalHeaderItem(row)
        if header is not None and band is not None:
            set_day_band(header, day_band_color(band))
