"""Fullscreen lightbox for previewing an image from `ImagePicker`."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common.avif_manager import load_image_pixmap
from harrix_swiss_knife.qt_emoji_icon import CLOSE_BUTTON_EMOJI, create_emoji_icon

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_SCREEN_MARGIN = 48
_CLOSE_BUTTON_SIZE = 40


class ImageLightboxDialog(QDialog):
    """Show an image at native size or fitted to the screen, with close / Escape."""

    def __init__(self, image_path: str | Path, parent: QWidget | None = None) -> None:
        """Build a modal dark overlay centered on the available screen."""
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(Path(image_path).name)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=False)
        self.setStyleSheet("ImageLightboxDialog { background-color: rgba(0, 0, 0, 220); }")
        self.setCursor(Qt.CursorShape.ArrowCursor)

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            self.setGeometry(available)
            max_width = max(100, available.width() - _SCREEN_MARGIN)
            max_height = max(100, available.height() - _SCREEN_MARGIN)
        else:
            max_width, max_height = 1280, 720
            self.resize(max_width, max_height)

        pixmap = load_image_pixmap(image_path)
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("background: transparent; border: none;")
        image_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        if pixmap is not None and not pixmap.isNull():
            if pixmap.width() <= max_width and pixmap.height() <= max_height:
                display = pixmap
            else:
                display = pixmap.scaled(
                    max_width,
                    max_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            image_label.setPixmap(display)
        else:
            image_label.setText(f"Could not load image:\n{image_path}")
            image_label.setStyleSheet("color: white; background: transparent; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(image_label, stretch=1)

        close_button = QPushButton(self)
        close_button.setIcon(create_emoji_icon(CLOSE_BUTTON_EMOJI, 22))
        close_button.setIconSize(QSize(22, 22))
        close_button.setFixedSize(_CLOSE_BUTTON_SIZE, _CLOSE_BUTTON_SIZE)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setToolTip("Close")
        close_button.setStyleSheet(
            "QPushButton {"
            " background: rgba(40, 40, 40, 200);"
            " border: 1px solid rgba(255, 255, 255, 80);"
            " border-radius: 8px;"
            " padding: 0;"
            "}"
            "QPushButton:hover { background: rgba(70, 70, 70, 230); }"
        )
        close_button.clicked.connect(self.accept)
        close_button.raise_()
        self._close_button = close_button
        self._position_close_button()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Close the lightbox on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        super().keyPressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Close when clicking the dimmed backdrop (not the close button)."""
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if child is self._close_button or (child is not None and self._close_button.isAncestorOf(child)):
                super().mouseReleaseEvent(event)
                return
            self.accept()
            return
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep the close button pinned to the top-right corner."""
        super().resizeEvent(event)
        self._position_close_button()

    def _position_close_button(self) -> None:
        margin = 16
        self._close_button.move(self.width() - _CLOSE_BUTTON_SIZE - margin, margin)


def show_image_lightbox(image_path: str | Path, parent: QWidget | None = None) -> None:
    """Open a modal lightbox for `image_path`."""
    path = Path(image_path)
    if not path.is_file():
        return
    dialog = ImageLightboxDialog(path, parent=parent)
    dialog.exec()
