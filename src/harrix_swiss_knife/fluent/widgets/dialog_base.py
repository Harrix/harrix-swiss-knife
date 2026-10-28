"""Modal Fluent dialog and its body / footer parts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.fluent.theme import bind_theme, enable_fluent_theme, is_fluent_themed, palette_for
from harrix_swiss_knife.fluent.tokens import (
    SPACE_M,
    SPACE_S,
    SPACE_XL,
)
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.buttons import FluentPrimaryButton
from harrix_swiss_knife.fluent.widgets.enums import TextStyle
from harrix_swiss_knife.fluent.widgets.text_base import FluentText

if TYPE_CHECKING:
    from PySide6.QtGui import QPaintEvent

_DIALOG_MIN_WIDTH = 320
_DIALOG_MAX_WIDTH = 548


class FluentDialog(QDialog):
    """Modal window dialog: subtitle, text, optional content, and a footer with buttons."""

    def __init__(
        self,
        title: str,
        content: str = "",
        parent: QWidget | None = None,
        *,
        primary_text: str = "OK",
        secondary_text: str = "Cancel",
    ) -> None:
        """Create a dialog (`exec()` returns `Accepted` for the primary button)."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(_DIALOG_MIN_WIDTH)
        self.setMaximumWidth(_DIALOG_MAX_WIDTH + 200)
        if parent is None or is_fluent_themed(parent):
            enable_fluent_theme(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._body = FluentDialogBody(title, content, self)
        layout.addWidget(self._body)
        self.content_layout = self._body.content_layout
        self.primary_button = self._body.primary
        self.secondary_button = self._body.secondary
        self.primary_button.setText(primary_text)
        self.secondary_button.setText(secondary_text)
        self.secondary_button.setVisible(bool(secondary_text))
        self.primary_button.clicked.connect(self.accept)
        self.secondary_button.clicked.connect(self.reject)
        self.primary_button.setDefault(True)


class FluentDialogBody(QWidget):
    """Title + content + footer used by both `FluentDialog` and `FluentContentDialog`."""

    def __init__(self, title: str, content: str, parent: QWidget) -> None:
        """Build the title, content text, and the OK / Cancel footer."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        top = QWidget(self)
        self.content_layout = QVBoxLayout(top)
        self.content_layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        self.content_layout.setSpacing(SPACE_M)
        self.title_label = FluentText(title, top, style=TextStyle.SUBTITLE)
        self.content_layout.addWidget(self.title_label)
        self.content_label = FluentText(content, top, word_wrap=True)
        self.content_label.setVisible(bool(content))
        self.content_layout.addWidget(self.content_label)
        layout.addWidget(top, 1)
        self.footer = FluentDialogFooter(self)
        layout.addWidget(self.footer)
        self.primary = FluentPrimaryButton("OK", self.footer)
        self.secondary = FluentPushButton("Cancel", self.footer)
        self.footer.row.addWidget(self.primary, 1)
        self.footer.row.addWidget(self.secondary, 1)


class FluentDialogFooter(QWidget):
    """Bottom strip of a dialog: `layer_alt` fill with right-aligned buttons."""

    def __init__(self, parent: QWidget) -> None:
        """Create the footer with an empty button row."""
        super().__init__(parent)
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        self.row.setSpacing(SPACE_S)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the footer fill and its top hairline."""
        palette = palette_for(self)
        painter = QPainter(self)
        painter.fillRect(self.rect(), palette.layer_alt_bg if not palette.dark else palette.solid_secondary_bg)
        painter.fillRect(0, 0, self.width(), 1, palette.card_stroke)
        painter.end()
