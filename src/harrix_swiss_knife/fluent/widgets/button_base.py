"""Icon mixin and the standard Fluent push button."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QAbstractButton, QPushButton, QWidget

from harrix_swiss_knife.fluent.style import (
    push_button_qss,
    themed_icon,
)
from harrix_swiss_knife.fluent.theme import bind_theme, palette_for
from harrix_swiss_knife.fluent.tokens import (
    ICON_SIZE,
)
from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon


class FluentIconMixin:
    """Keep a Lucide icon on a button in the current text color."""

    _icon_name: str = ""
    _icon_on_accent: bool = False

    def _sync_icon(self) -> None:
        button = self
        if not isinstance(button, QAbstractButton) or not self._icon_name:
            return
        palette = palette_for(button)
        if self._icon_on_accent:
            button.setIcon(create_lucide_icon(self._icon_name, ICON_SIZE, color=palette.text_on_accent))
        else:
            button.setIcon(themed_icon(self._icon_name, palette))
        button.setIconSize(QSize(ICON_SIZE, ICON_SIZE))


class FluentPushButton(FluentIconMixin, QPushButton):
    """Standard neutral Fluent button with an optional Lucide icon."""

    def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        """Create a standard button.

        Args:

        - `text` (`str`): Caption.
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`str`): Optional Lucide icon ID.

        """
        super().__init__(text, parent)
        self._icon_name = icon
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoDefault(False)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome and icon colors."""
        self.setStyleSheet(push_button_qss(palette_for(self)))
        self._sync_icon()

    def set_icon_name(self, name: str) -> None:
        """Set the Lucide icon ID."""
        self._icon_name = name
        self._sync_icon()
