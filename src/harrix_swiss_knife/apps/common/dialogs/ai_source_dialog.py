"""Dialog for raw text and/or image input before BotHub processing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.widgets.image_drop_widget import ImageDropWidget

if TYPE_CHECKING:
    from PySide6.QtWidgets import QPushButton


SEND_TO_AI_BUTTON_STYLE = """QPushButton {
    background-color: #C1ECDD;
}
QPushButton:hover {
    background-color: #D1F5E8;
}
QPushButton:pressed {
    background-color: #A8E0C7;
}"""


class AiSourceDialog(QDialog):
    """Modal dialog to collect source text and/or an image for BotHub."""

    SKIP_MANUAL: int = 2

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add with AI",
        description: str = "",
        placeholder: str = "",
        send_button_text: str = "Send to AI",
    ) -> None:
        """Initialize the AI source dialog."""
        super().__init__(parent)
        self._title = title
        self._description = description
        self._placeholder = placeholder
        self._send_button_text = send_button_text
        self._raw_text: str = ""
        self._image_data: tuple[bytes, str] | None = None
        self._setup_ui()

    def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None:
        """Return image bytes and MIME type if an image was provided."""
        return self._image_data

    def get_raw_text(self) -> str:
        """Return raw text entered by the user."""
        return self._raw_text

    def _on_accept(self) -> None:
        self._raw_text = self.text_edit.toPlainText().strip()
        self._image_data = self.image_widget.get_image_bytes_and_mime()
        if not self._raw_text and not self._image_data:
            return
        self.accept()

    def _on_skip_to_manual(self) -> None:
        self.done(self.SKIP_MANUAL)

    def _setup_ui(self) -> None:
        self.setWindowTitle(self._title)
        self.setMinimumSize(640, 520)
        self.setModal(True)

        layout = QVBoxLayout(self)

        if self._description:
            text_label = QLabel(self._description)
            text_label.setWordWrap(True)
            layout.addWidget(text_label)

        self.text_edit = QPlainTextEdit()
        if self._placeholder:
            self.text_edit.setPlaceholderText(self._placeholder)
        self.text_edit.setMinimumHeight(120)
        self.text_edit.textChanged.connect(self._update_ok_enabled)
        layout.addWidget(self.text_edit)

        image_label = QLabel("Image (drag, paste Ctrl+V, or select file):")
        layout.addWidget(image_label)

        self.image_widget = ImageDropWidget()
        self.image_widget.image_changed.connect(self._update_ok_enabled)
        layout.addWidget(self.image_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._ok_button: QPushButton = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_button.setText(self._send_button_text)
        send_to_ai_font = QFont()
        send_to_ai_font.setBold(True)
        self._ok_button.setFont(send_to_ai_font)
        self._ok_button.setStyleSheet(SEND_TO_AI_BUTTON_STYLE)
        self._ok_button.setEnabled(False)
        skip_button = buttons.addButton("Enter Text Manually", QDialogButtonBox.ButtonRole.ActionRole)
        skip_button.clicked.connect(self._on_skip_to_manual)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _update_ok_enabled(self) -> None:
        has_text = bool(self.text_edit.toPlainText().strip())
        has_image = self.image_widget.has_image()
        self._ok_button.setEnabled(has_text or has_image)
