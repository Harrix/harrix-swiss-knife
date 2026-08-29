"""Preview dialog for a captured screenshot region."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

import harrix_pylib as h
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.actions.common.text_result_dialog import (
    COPY_BUTTON_EMOJI,
    COPY_BUTTON_LABEL,
    add_ok_button,
)
from harrix_swiss_knife.apps.common.qt_main_window import apply_app_window_size_and_position
from harrix_swiss_knife.qt_emoji_icon import SAVE_BUTTON_EMOJI, make_emoji_push_button
from harrix_swiss_knife.screenshot.dated_image_path import images_folder, next_dated_image_path
from harrix_swiss_knife.screenshot.preview_canvas import ScreenshotPreviewCanvas

if TYPE_CHECKING:
    from PySide6.QtGui import QImage

_SAVE_BUTTON_LABEL = "Save as…"
_MARKDOWN_AI_EMOJI = "🤖"
_MARKDOWN_OCR_EMOJI = "🔤"
_VK_S = 0x53
_KEY_CYRILLIC_YERU = 0x042B  # Cyrillic yeru (same physical key as Latin S)  # ignore: HP001


class ScreenshotPreviewDialog(QDialog):
    """Show a captured image with Copy / Save / Markdown OCR / OK actions."""

    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        """Create the preview dialog for `image`."""
        super().__init__(parent)
        self.setWindowTitle("Screenshot")
        qt_modality.set_owner_window_modal(self)
        self._image = image

        self._canvas = ScreenshotPreviewCanvas(image, self)
        self._status = QLabel(self)
        self._status.setWordWrap(True)
        self._status.setText("Ctrl+wheel zoom · Middle-drag pan · Ctrl+S save to images")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self._status, stretch=1)
        copy_button = make_emoji_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_EMOJI)
        copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_button)

        save_button = make_emoji_push_button(_SAVE_BUTTON_LABEL, SAVE_BUTTON_EMOJI)
        save_button.clicked.connect(self._save_as)
        button_layout.addWidget(save_button)

        ai_button = make_emoji_push_button("Recognize text (AI)", _MARKDOWN_AI_EMOJI)
        ai_button.setToolTip("Recognize text (AI)…")
        ai_button.clicked.connect(self._run_markdown_with_ai)
        button_layout.addWidget(ai_button)

        ocr_button = make_emoji_push_button("Recognize text (OCR)", _MARKDOWN_OCR_EMOJI)
        ocr_button.setToolTip("Recognize text (OCR, local)…")
        ocr_button.clicked.connect(self._run_markdown_with_ocr)
        button_layout.addWidget(ocr_button)

        add_ok_button(self, button_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(self._canvas, stretch=1)
        layout.addLayout(button_layout)

        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        save_shortcut.activated.connect(self._save_to_images)

        apply_app_window_size_and_position(self)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Save on Ctrl+S / Ctrl+Yeru (layout-independent via virtual key)."""  # ignore: HP001
        if _is_ctrl_s(event):
            self._save_to_images()
            event.accept()
            return
        super().keyPressEvent(event)

    def _copy_to_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setImage(self._image)

    def _run_markdown_with_ai(self) -> None:
        path = self._save_temp_png()
        if path is None:
            return
        self.accept()

        def run() -> None:
            # Local import: actions.images.__init__ pulls screenshot_region -> this package.
            from harrix_swiss_knife.actions.images.recognize_text_with_ai import (  # noqa: PLC0415
                OnRecognizeTextWithAI,
            )

            OnRecognizeTextWithAI()(image_paths=[path])

        QTimer.singleShot(0, run)

    def _run_markdown_with_ocr(self) -> None:
        path = self._save_temp_png()
        if path is None:
            return
        self.accept()

        def run() -> None:
            # Local import: actions.images.__init__ pulls screenshot_region -> this package.
            from harrix_swiss_knife.actions.images.recognize_text_with_ocr import (  # noqa: PLC0415
                OnRecognizeTextWithOcr,
            )

            OnRecognizeTextWithOcr()(image_paths=[path])

        QTimer.singleShot(0, run)

    def _save_as(self) -> None:
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save screenshot",
            "screenshot.png",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*)",
        )
        if not path:
            return
        if self._image.save(path):
            self._status.setText(f"Saved: {path}")

    def _save_temp_png(self) -> str | None:
        with NamedTemporaryFile(suffix=".png", delete=False) as handle:
            temp_path = Path(handle.name)
        if self._image.save(str(temp_path)):
            return str(temp_path)
        return None

    def _save_to_images(self) -> None:
        folder = images_folder(h.dev.get_project_root())
        path = next_dated_image_path(folder)
        if not self._image.save(str(path)):
            self._status.setText(f"Could not save to {path}")
            return
        self._status.setText(f"Saved: {path.name}")


def _is_ctrl_s(event: QKeyEvent) -> bool:
    if event.modifiers() & Qt.KeyboardModifier.AltModifier:
        return False
    if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
        return False
    if event.nativeVirtualKey() == _VK_S:
        return True
    return event.key() in {int(Qt.Key.Key_S), _KEY_CYRILLIC_YERU}
