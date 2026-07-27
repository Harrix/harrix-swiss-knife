"""Thumbnail tile used by multi-image `ImagePicker`."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton

from harrix_swiss_knife.apps.common.avif_manager import load_image_pixmap
from harrix_swiss_knife.apps.common.widgets.image_lightbox_dialog import show_image_lightbox

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QWidget

_THUMB_SIZE = 96
_REMOVE_BTN_SIZE = 24


class ImageThumbnailItem(QFrame):
    """Single image thumbnail with a remove button in the top-right corner."""

    def __init__(
        self,
        image_path: str,
        *,
        on_remove: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        """Build a thumbnail tile with a remove button."""
        super().__init__(parent)
        self.image_path = image_path
        self._on_remove = on_remove
        self.setFixedSize(_THUMB_SIZE, _THUMB_SIZE)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("ImageThumbnailItem { border: none; background: transparent; }")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to preview")

        grid = QGridLayout(self)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(0)

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        pixmap = load_image_pixmap(image_path)
        if pixmap is not None and not pixmap.isNull():
            thumb_label.setPixmap(
                pixmap.scaled(
                    _THUMB_SIZE - 8,
                    _THUMB_SIZE - 8,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            thumb_label.setText(Path(image_path).name)
        grid.addWidget(thumb_label, 0, 0)

        remove_btn = QPushButton("×")  # noqa: RUF001
        remove_btn.setFixedSize(_REMOVE_BTN_SIZE, _REMOVE_BTN_SIZE)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet(
            "QPushButton { background: #e53935; color: white; border: none; border-radius: 12px; "
            "font-size: 16px; font-weight: bold; padding: 0; min-width: 0; min-height: 0; }"
            "QPushButton:hover { background: #c62828; }"
        )
        remove_btn.clicked.connect(self._handle_remove)
        grid.addWidget(remove_btn, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self._remove_button = remove_btn

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Open lightbox on left click; ignore clicks on the remove button."""
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if child is self._remove_button or (child is not None and self._remove_button.isAncestorOf(child)):
                super().mouseReleaseEvent(event)
                return
            show_image_lightbox(self.image_path, parent=self.window())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _handle_remove(self) -> None:
        self._on_remove(self.image_path)
