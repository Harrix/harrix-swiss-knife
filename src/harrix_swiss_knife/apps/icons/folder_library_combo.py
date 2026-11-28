"""Folder library QComboBox with a sticky “Add folder…” action in the popup."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QBoxLayout, QComboBox, QPushButton

from harrix_swiss_knife.apps.common.ui_chrome import HAIRLINE, INPUT_BORDER, SURFACE, button_idle_qss
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_ADD_FOLDER_LABEL = "Add folder…"
_ADD_FOLDER_ICON = "folder-plus"
_FOOTER_ICON_SIZE = 16
_FOOTER_MIN_HEIGHT = 32


class FolderLibraryCombo(QComboBox):
    """Combo of icon library roots with a sticky footer to open another folder.

    The footer sits below the scrollable popup list so it stays visible even when
    there are many pinned libraries.

    """

    add_folder_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the combo; call `showPopup` to attach the sticky footer."""
        super().__init__(parent)
        self._footer: QPushButton | None = None
        self._footer_attached = False

    def hidePopup(self) -> None:  # noqa: N802
        """Hide the sticky footer with the popup."""
        footer = self._footer
        if footer is not None:
            footer.hide()
        super().hidePopup()

    def showPopup(self) -> None:  # noqa: N802
        """Show the popup, then attach or reveal the sticky Add folder footer."""
        super().showPopup()
        QTimer.singleShot(0, self._attach_or_show_footer)

    def _attach_or_show_footer(self) -> None:
        view = self.view()
        if view is None:
            return
        container = view.parentWidget()
        if container is None:
            return
        layout = container.layout()
        footer = self._ensure_footer(container)
        if isinstance(layout, QBoxLayout) and not self._footer_attached:
            layout.addWidget(footer)
            self._footer_attached = True
            # Grow the popup so the footer is not clipped under the list view.
            extra = footer.sizeHint().height()
            if extra <= 0:
                extra = _FOOTER_MIN_HEIGHT
            container.resize(container.width(), container.height() + extra)
        elif footer.parent() is not container:
            footer.setParent(container)
        footer.show()
        footer.raise_()

    def _ensure_footer(self, container: QWidget) -> QPushButton:
        footer = self._footer
        if footer is not None:
            return footer
        footer = QPushButton(_ADD_FOLDER_LABEL, container)
        footer.setObjectName("vectorIconsAddFolderFooter")
        footer.setCursor(Qt.CursorShape.PointingHandCursor)
        footer.setMinimumHeight(_FOOTER_MIN_HEIGHT)
        footer.setStyleSheet(
            button_idle_qss() + f" QPushButton#vectorIconsAddFolderFooter {{"
            f" border-top: 1px solid {INPUT_BORDER};"
            f" border-left: none; border-right: none; border-bottom: none;"
            f" border-radius: 0px;"
            f" background-color: {SURFACE};"
            f" text-align: left;"
            f" padding-left: 10px;"
            f"}}"
            f" QPushButton#vectorIconsAddFolderFooter:hover {{"
            f" background-color: {HAIRLINE};"
            f"}}"
        )
        apply_lucide_button_icon(footer, _ADD_FOLDER_ICON, icon_size=_FOOTER_ICON_SIZE)
        footer.setToolTip("Choose another icons library folder to open")
        footer.clicked.connect(self._on_footer_clicked)
        self._footer = footer
        return footer

    def _on_footer_clicked(self) -> None:
        self.hidePopup()
        self.add_folder_requested.emit()
