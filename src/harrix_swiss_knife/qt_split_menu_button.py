"""Split button: primary action on the left, menu arrow on the right."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSizePolicy, QToolButton, QWidget

from harrix_swiss_knife.qt_lucide_icon import DEFAULT_LUCIDE_BUTTON_ICON_SIZE, apply_lucide_button_icon

if TYPE_CHECKING:
    from PySide6.QtGui import QColor, QIcon
    from PySide6.QtWidgets import QMenu

_ARROW_WIDTH = 28
_ARROW_ICON_SIZE = 16
_SEPARATOR_COLOR = "#c0c0c0"
_STYLE = f"""
SplitMenuButton {{
    border: 1px solid #adadad;
    border-radius: 4px;
    background-color: #f3f3f3;
}}
SplitMenuButton:hover {{
    background-color: #e9e9e9;
    border-color: #9a9a9a;
}}
SplitMenuButton QPushButton#splitMenuMain {{
    border: none;
    background: transparent;
    padding: 4px 10px;
}}
SplitMenuButton QToolButton#splitMenuArrow {{
    border: none;
    background: transparent;
    padding: 4px 2px;
}}
SplitMenuButton QPushButton#splitMenuMain:hover,
SplitMenuButton QToolButton#splitMenuArrow:hover {{
    background-color: rgba(0, 0, 0, 0.06);
}}
SplitMenuButton QPushButton#splitMenuMain:pressed,
SplitMenuButton QToolButton#splitMenuArrow:pressed {{
    background-color: rgba(0, 0, 0, 0.10);
}}
SplitMenuButton QFrame#splitMenuSeparator {{
    background-color: {_SEPARATOR_COLOR};
    border: none;
    max-width: 1px;
    min-width: 1px;
}}
"""


class SplitMenuButton(QWidget):
    """Push-button left zone plus a menu arrow separated by a vertical line.

    Clicking the main zone emits `clicked`. Clicking the arrow opens `menu()`.
    Use this wherever a default action and a related dropdown are needed.

    """

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None, text: str = "") -> None:
        """Build the split chrome with an empty optional menu."""
        super().__init__(parent)
        self.setObjectName("splitMenuButton")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(_STYLE)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._menu: QMenu | None = None

        self._main = QPushButton(text, self)
        self._main.setObjectName("splitMenuMain")
        self._main.setCursor(Qt.CursorShape.PointingHandCursor)
        self._main.setAutoDefault(False)
        self._main.setDefault(False)
        self._main.clicked.connect(self.clicked.emit)

        self._separator = QFrame(self)
        self._separator.setObjectName("splitMenuSeparator")
        self._separator.setFrameShape(QFrame.Shape.NoFrame)
        self._separator.setFixedWidth(1)

        self._arrow = QToolButton(self)
        self._arrow.setObjectName("splitMenuArrow")
        self._arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self._arrow.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._arrow.setAutoRaise(True)
        self._arrow.setFixedWidth(_ARROW_WIDTH)
        self._arrow.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        apply_lucide_button_icon(self._arrow, "chevron-down", icon_size=_ARROW_ICON_SIZE)
        self._arrow.clicked.connect(self._show_menu)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._main, stretch=1)
        layout.addWidget(self._separator)
        layout.addWidget(self._arrow)

        self.setFocusProxy(self._main)

    @property
    def arrow_button(self) -> QToolButton:
        """Return the menu-arrow button."""
        return self._arrow

    def icon(self) -> QIcon:
        """Return the main-zone icon."""
        return self._main.icon()

    @property
    def main_button(self) -> QPushButton:
        """Return the primary-action button (text / icon target)."""
        return self._main

    def menu(self) -> QMenu | None:
        """Return the dropdown menu, or `None` when unset."""
        return self._menu

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Prefer the combined main + separator + arrow width."""
        return self.sizeHint()

    def setIcon(self, icon: QIcon) -> None:  # noqa: N802
        """Set the Lucide / chrome icon on the main zone."""
        self._main.setIcon(icon)

    def setIconSize(self, size: QSize) -> None:  # noqa: N802
        """Set the main-zone icon size."""
        self._main.setIconSize(size)

    def setMenu(self, menu: QMenu | None) -> None:  # noqa: N802
        """Attach the dropdown shown when the arrow is clicked."""
        self._menu = menu
        if menu is not None:
            menu.setParent(self)

    def setText(self, text: str) -> None:  # noqa: N802
        """Set the main-zone caption."""
        self._main.setText(text)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the size of main zone plus separator and arrow."""
        main = self._main.sizeHint()
        arrow = self._arrow.sizeHint()
        height = max(main.height(), arrow.height(), self._separator.sizeHint().height())
        width = main.width() + self._separator.width() + max(arrow.width(), _ARROW_WIDTH)
        return QSize(width, height)

    def text(self) -> str:
        """Return the main-zone caption."""
        return self._main.text()

    def _show_menu(self) -> None:
        if self._menu is None:
            return
        self._menu.exec(self._arrow.mapToGlobal(QPoint(0, self._arrow.height())))


def make_lucide_split_menu_button(
    label: str,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
    color: QColor | str | None = None,
    parent: QWidget | None = None,
) -> SplitMenuButton:
    """Create a split menu button with a Lucide icon on the main zone."""
    button = SplitMenuButton(parent, text=label)
    apply_lucide_button_icon(button.main_button, name, icon_size=icon_size, color=color)
    return button
