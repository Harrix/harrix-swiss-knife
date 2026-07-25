"""Preview dialog for a captured screenshot region."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.actions.text_result_dialog import (
    COPY_BUTTON_EMOJI,
    COPY_BUTTON_LABEL,
    add_ok_button,
)
from harrix_swiss_knife.qt_emoji_icon import SAVE_BUTTON_EMOJI, make_emoji_push_button

_MAX_PREVIEW_SIDE = 900
_SAVE_BUTTON_LABEL = "Save as…"
_MARKDOWN_AI_EMOJI = "🤖"
_MARKDOWN_OCR_EMOJI = "🔤"


class ScreenshotPreviewDialog(QDialog):
    """Show a captured image with Copy / Save / Markdown OCR / OK actions."""

    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        """Create the preview dialog for `image`."""
        super().__init__(parent)
        self.setWindowTitle("Screenshot")
        self.setModal(True)
        self._image = image

        preview = QLabel()
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap.fromImage(image)
        if max(pixmap.width(), pixmap.height()) > _MAX_PREVIEW_SIDE:
            pixmap = pixmap.scaled(
                _MAX_PREVIEW_SIDE,
                _MAX_PREVIEW_SIDE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        preview.setPixmap(pixmap)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(preview)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        copy_button = make_emoji_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_EMOJI)
        copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_button)

        save_button = make_emoji_push_button(_SAVE_BUTTON_LABEL, SAVE_BUTTON_EMOJI)
        save_button.clicked.connect(self._save_as)
        button_layout.addWidget(save_button)

        ai_button = make_emoji_push_button("Markdown (AI)", _MARKDOWN_AI_EMOJI)
        ai_button.setToolTip("Image to Markdown (OCR, AI)…")
        ai_button.clicked.connect(self._run_markdown_with_ai)
        button_layout.addWidget(ai_button)

        ocr_button = make_emoji_push_button("Markdown (OCR)", _MARKDOWN_OCR_EMOJI)
        ocr_button.setToolTip("Image to Markdown (OCR, local)…")
        ocr_button.clicked.connect(self._run_markdown_with_ocr)
        button_layout.addWidget(ocr_button)

        add_ok_button(self, button_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.addLayout(button_layout)

        self.resize(min(pixmap.width() + 40, 960), min(pixmap.height() + 100, 720))

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
            from harrix_swiss_knife.actions.images.image_to_markdown_with_ai import (  # noqa: PLC0415
                OnImageToMarkdownWithAI,
            )

            OnImageToMarkdownWithAI()(image_paths=[path])

        QTimer.singleShot(0, run)

    def _run_markdown_with_ocr(self) -> None:
        path = self._save_temp_png()
        if path is None:
            return
        self.accept()

        def run() -> None:
            from harrix_swiss_knife.actions.images.image_to_markdown_with_ocr import (  # noqa: PLC0415
                OnImageToMarkdownWithOcr,
            )

            OnImageToMarkdownWithOcr()(image_paths=[path])

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
        self._image.save(path)

    def _save_temp_png(self) -> str | None:
        with NamedTemporaryFile(suffix=".png", delete=False) as handle:
            temp_path = Path(handle.name)
        if self._image.save(str(temp_path)):
            return str(temp_path)
        return None
