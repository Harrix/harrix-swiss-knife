"""Shared white command-section cards for icon grids (main window, quick launcher)."""

from __future__ import annotations

import contextlib

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QFrame, QLabel, QListWidget, QSizePolicy, QVBoxLayout, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import action_card_selection_qss, apply_readable_selection_palette
from harrix_swiss_knife.fluent.theme import bind_theme
from harrix_swiss_knife.qt_action_card_grid import CARD_GRID_CELL_HEIGHT
from harrix_swiss_knife.qt_flat_scrollbar import with_flat_scrollbars

COMMAND_SECTION_OBJECT_NAME = "commandSection"
COMMAND_SECTION_DIVIDER_OBJECT_NAME = "commandSectionDivider"
COMMAND_SECTION_BORDER_COLOR = "#c0c0c0"
_COMMAND_SECTION_THEME_FLAG = "_command_section_theme_bound"
_COMMAND_SECTION_LABEL_STYLE = (
    f"#{COMMAND_SECTION_OBJECT_NAME} > QLabel {{ background: transparent; padding: 4px 8px 0px 8px;}}"
)


def apply_opaque_white(widget: QWidget) -> None:
    """Paint an opaque card surface without stylesheets (keeps native scrollbars)."""
    palette = widget.palette()
    fill = _command_section_surface_qcolor()
    palette.setColor(QPalette.ColorRole.Window, fill)
    palette.setColor(QPalette.ColorRole.Base, fill)
    widget.setAutoFillBackground(True)
    widget.setPalette(palette)


def count_icon_grid_first_row(grid: QListWidget) -> int:
    """Return how many icon cards Qt placed on the first row."""
    if grid.count() == 0:
        return 0
    grid.doItemsLayout()
    first = grid.item(0)
    if first is None:
        return 0
    first_top = grid.visualItemRect(first).top()
    count = 0
    for index in range(grid.count()):
        item = grid.item(index)
        if item is None:
            continue
        if grid.visualItemRect(item).top() > first_top + 4:
            break
        count += 1
    return count


def create_command_section(
    *,
    title: str | None = None,
    bordered: bool = True,
) -> tuple[QFrame, QLabel | None, QVBoxLayout]:
    """Create a white section card for an icon command grid.

    Args:

    - `title` (`str | None`): Optional bold section heading.
    - `bordered` (`bool`): Draw the gray rounded outline. Defaults to `True`.
      Pass `False` for the tray commands window and Quick Launcher overlays.

    Returns:

    - `(frame, label, layout)`: Add the grid with `layout.addWidget(grid)`.
      `label` is `None` when `title` is omitted.

    """
    frame = QFrame()
    frame.setObjectName(COMMAND_SECTION_OBJECT_NAME)
    frame.setFrameShape(QFrame.Shape.NoFrame)
    frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def refresh_style() -> None:
        frame.setStyleSheet(_command_section_stylesheet(bordered=bordered))

    refresh_style()
    if not getattr(frame, _COMMAND_SECTION_THEME_FLAG, False):
        bind_theme(frame, refresh_style)
        setattr(frame, _COMMAND_SECTION_THEME_FLAG, True)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(8, 4, 8, 8)
    layout.setSpacing(4)

    label: QLabel | None = None
    if title is not None:
        label = QLabel(title)
        font = QFont(label.font())
        font.setBold(True)
        grow_qfont(font)
        label.setFont(font)
        layout.addWidget(label)

    return frame, label, layout


def create_command_section_divider() -> QWidget:
    """Return a 1px horizontal rule in the command-section border color.

    Uses palette fill instead of a stylesheet background: stylesheet
    `background-color` on a frameless `QFrame` often paints nothing unless
    `WA_StyledBackground` is set, which made the tray dividers invisible.

    """
    line = QWidget()
    line.setObjectName(COMMAND_SECTION_DIVIDER_OBJECT_NAME)
    line.setFixedHeight(1)
    line.setMinimumHeight(1)
    line.setMaximumHeight(1)
    line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def refresh_divider() -> None:
        palette = line.palette()
        color = _command_section_border_qcolor()
        palette.setColor(QPalette.ColorRole.Window, color)
        palette.setColor(QPalette.ColorRole.Base, color)
        line.setAutoFillBackground(True)
        line.setPalette(palette)

    refresh_divider()
    if not getattr(line, _COMMAND_SECTION_THEME_FLAG, False):
        bind_theme(line, refresh_divider)
        setattr(line, _COMMAND_SECTION_THEME_FLAG, True)
    return line


def fit_icon_grid_height(grid: QListWidget) -> None:
    """Set grid height from laid-out icon rows; clear leftover internal scroll range."""
    if not grid.isVisible():
        return
    if grid.count() == 0:
        grid.setFixedHeight(0)
        return

    height = measure_icon_grid_height(grid)
    grid.setFixedHeight(height)
    grid.verticalScrollBar().setRange(0, 0)
    grid.horizontalScrollBar().setRange(0, 0)


def grow_qfont(font: QFont, *, delta: int = 1, fallback_point_size: int = 10) -> QFont:
    """Increase font size without calling `setPointSize` on a pixel-sized font.

    Windows system fonts often have `pointSize() == -1` and a pixel size instead.
    Passing that value to `QFont.setPointSize` logs
    `Point size <= 0 (-1)`.

    Args:

    - `font` (`QFont`): Font to grow in place.
    - `delta` (`int`): Size increment. Defaults to `1`.
    - `fallback_point_size` (`int`): Point size used when the font has neither
      a point size nor a pixel size. Defaults to `10`.

    Returns:

    - `QFont`: The same `font` instance after the size change.

    """
    point_size = font.pointSize()
    if point_size > 0:
        font.setPointSize(point_size + delta)
        return font
    pixel_size = font.pixelSize()
    if pixel_size > 0:
        font.setPixelSize(pixel_size + delta)
        return font
    font.setPointSize(max(1, fallback_point_size + delta))
    return font


def measure_icon_grid_height(grid: QListWidget) -> int:
    """Return pixel height needed for all icon cards in the grid."""
    if grid.count() == 0:
        return 0

    grid.doItemsLayout()
    item_bottoms = [
        grid.visualItemRect(grid.item(index)).bottom() for index in range(grid.count()) if grid.item(index) is not None
    ]
    return max(item_bottoms, default=CARD_GRID_CELL_HEIGHT - 1) + 1 + 4


def prepare_icon_grid(grid: QListWidget, *, event_filter: QObject | None = None) -> None:
    """Make an icon grid frameless and non-scrolling (outer scroll owns the wheel)."""
    style_transparent_icon_grid(grid)
    grid.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    grid.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    grid.verticalScrollBar().setEnabled(False)
    grid.horizontalScrollBar().setEnabled(False)
    if event_filter is not None:
        grid.installEventFilter(event_filter)
        grid.viewport().installEventFilter(event_filter)


def style_transparent_icon_grid(grid: QListWidget) -> None:
    """Keep icon grids frameless so the parent section owns chrome."""
    grid.setAutoFillBackground(False)
    grid.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)
    grid.setStyleSheet(with_flat_scrollbars(action_card_selection_qss()))
    apply_readable_selection_palette(grid)


def _command_section_border_qcolor() -> QColor:
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.theme import FluentTheme, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        if palette.dark:
            return mix(palette.window_bg, palette.control_stroke)
    return QColor(COMMAND_SECTION_BORDER_COLOR)


def _command_section_stylesheet(*, bordered: bool) -> str:
    bg = _command_section_surface_qcolor().name(QColor.NameFormat.HexRgb)
    if bordered:
        border = _command_section_border_qcolor().name(QColor.NameFormat.HexRgb)
        card = (
            f"#{COMMAND_SECTION_OBJECT_NAME} {{"
            f" background-color: {bg};"
            f" border: 1px solid {border};"
            " border-radius: 8px;"
            "}"
        )
    else:
        card = f"#{COMMAND_SECTION_OBJECT_NAME} {{ background-color: {bg}; border: none;}}"
    return f"{card}{_COMMAND_SECTION_LABEL_STYLE}"


def _command_section_surface_qcolor() -> QColor:
    """Opaque card fill (white in light, Fluent card mix in dark)."""
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.theme import FluentTheme, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        if palette.dark:
            return mix(palette.window_bg, palette.card_bg)
    return QColor("#ffffff")
