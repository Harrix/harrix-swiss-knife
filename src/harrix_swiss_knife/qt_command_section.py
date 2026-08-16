"""Shared white command-section cards for icon grids (main window, quick launcher)."""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QFrame, QLabel, QListWidget, QSizePolicy, QVBoxLayout, QWidget

from harrix_swiss_knife.qt_action_card_grid import CARD_GRID_CELL_HEIGHT

COMMAND_SECTION_OBJECT_NAME = "commandSection"
COMMAND_SECTION_STYLE = (
    f"#{COMMAND_SECTION_OBJECT_NAME} {{"
    " background-color: #ffffff;"
    " border: 1px solid #c0c0c0;"
    " border-radius: 8px;"
    "}"
    f"#{COMMAND_SECTION_OBJECT_NAME} > QLabel {{"
    " background: transparent;"
    " padding: 4px 8px 0px 8px;"
    "}"
)


def apply_opaque_white(widget: QWidget) -> None:
    """Paint an opaque white background without stylesheets (keeps native scrollbars)."""
    palette = widget.palette()
    white = QColor("#ffffff")
    palette.setColor(QPalette.ColorRole.Window, white)
    palette.setColor(QPalette.ColorRole.Base, white)
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


def create_command_section(*, title: str | None = None) -> tuple[QFrame, QLabel | None, QVBoxLayout]:
    """Create a bordered white section card for an icon command grid.

    Returns:

    - `(frame, label, layout)`: Add the grid with `layout.addWidget(grid)`.
      `label` is `None` when `title` is omitted.

    """
    frame = QFrame()
    frame.setObjectName(COMMAND_SECTION_OBJECT_NAME)
    frame.setFrameShape(QFrame.Shape.NoFrame)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    frame.setStyleSheet(COMMAND_SECTION_STYLE)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(8, 4, 8, 8)
    layout.setSpacing(4)

    label: QLabel | None = None
    if title is not None:
        label = QLabel(title)
        font = QFont(label.font())
        font.setBold(True)
        font.setPointSize(font.pointSize() + 1)
        label.setFont(font)
        layout.addWidget(label)

    return frame, label, layout


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
    """Keep icon grids frameless so section cards own the border."""
    grid.setAutoFillBackground(False)
    grid.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)
    grid.setStyleSheet(
        "QListWidget {"
        " background: transparent;"
        " border: none;"
        "}"
        "QListWidget::item {"
        " padding-top: 0px;"
        " padding-bottom: 0px;"
        " margin: 0px;"
        "}",
    )
