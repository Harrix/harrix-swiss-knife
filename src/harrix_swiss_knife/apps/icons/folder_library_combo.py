"""Folder library QComboBox with a sticky “Add folder…” action in the popup."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QBoxLayout, QComboBox, QPushButton

from harrix_swiss_knife.apps.common.ui_chrome import HAIRLINE, MUTED_TEXT, SELECTION_HOVER

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_ADD_FOLDER_LABEL = "+ Add folder…"
_FOOTER_MIN_HEIGHT = 24


class FolderLibraryCombo(QComboBox):
    """Combo of icon library roots with a sticky footer to open another folder.

    The footer sits below the scrollable popup list so it stays visible even when
    there are many pinned libraries. It is styled like a list row, not a toolbar
    button, so it matches the folder names above.

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
        self._match_footer_to_list_row(footer, view)
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
        footer.setFlat(True)
        footer.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        footer.setStyleSheet(
            f"QPushButton#vectorIconsAddFolderFooter {{"
            f" background: transparent;"
            f" border: none;"
            f" border-top: 1px solid {HAIRLINE};"
            f" border-radius: 0px;"
            f" color: {MUTED_TEXT};"
            f" text-align: left;"
            f" padding: 2px 8px;"
            f" font-weight: normal;"
            f"}}"
            f"QPushButton#vectorIconsAddFolderFooter:hover {{"
            f" background-color: {SELECTION_HOVER};"
            f" color: {MUTED_TEXT};"
            f"}}"
            f"QPushButton#vectorIconsAddFolderFooter:pressed {{"
            f" background-color: {SELECTION_HOVER};"
            f"}}"
        )
        footer.setToolTip("Choose another icons library folder to open")
        footer.clicked.connect(self._on_footer_clicked)
        self._footer = footer
        return footer

    def _match_footer_to_list_row(self, footer: QPushButton, view: QWidget) -> None:
        """Align footer height with a popup list row when possible."""
        row_height = 0
        size_hint_for_row = getattr(view, "sizeHintForRow", None)
        if callable(size_hint_for_row) and self.count() > 0:
            row_height = int(size_hint_for_row(0))
        if row_height <= 0:
            row_height = _FOOTER_MIN_HEIGHT
        footer.setMinimumHeight(row_height)
        footer.setMaximumHeight(row_height)

    def _on_footer_clicked(self) -> None:
        self.hidePopup()
        self.add_folder_requested.emit()
