"""Configurable dialog for optional text and/or image input."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.widgets.image_picker import ImagePicker, ImagePickerMode
from harrix_swiss_knife.qt_emoji_icon import make_emoji_push_button

SEND_TO_AI_BUTTON_STYLE = """QPushButton {
    background-color: #C1ECDD;
}
QPushButton:hover {
    background-color: #D1F5E8;
}
QPushButton:pressed {
    background-color: #A8E0C7;
}"""


class TextImageSourceDialog(QDialog):
    """Modal dialog to collect optional text and/or images.

    Shared by apps (Food/Finance Add with AI) and actions that need the same UI.

    """

    SKIP_MANUAL: int = 2

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Source input",
        description: str = "",
        placeholder: str = "",
        show_text: bool = True,
        text_required: bool = False,
        show_images: bool = True,
        images_required: bool = False,
        image_mode: ImagePickerMode = ImagePickerMode.MULTI,
        image_label: str | None = "Images (drag, paste Ctrl+V, or select files):",
        show_skip_manual: bool = False,
        skip_manual_button_text: str = "Enter Text Manually",
        accept_button_text: str = "OK",
        accept_button_emoji: str = "✅",
        accept_button_style: str | None = None,
        max_image_side: int | None = None,
        initial_image_paths: list[str] | None = None,
        initial_image_path: str | None = None,
    ) -> None:
        """Initialize the text/image source dialog."""
        super().__init__(parent)
        self._title = title
        self._description = description
        self._placeholder = placeholder
        self._show_text = show_text
        self._text_required = text_required
        self._show_images = show_images
        self._images_required = images_required
        self._image_mode = image_mode
        self._image_label = image_label
        self._show_skip_manual = show_skip_manual
        self._skip_manual_button_text = skip_manual_button_text
        self._accept_button_text = accept_button_text
        self._accept_button_emoji = accept_button_emoji
        self._accept_button_style = accept_button_style
        self._max_image_side = max_image_side

        paths = list(initial_image_paths or [])
        if initial_image_path and initial_image_path not in paths:
            paths.insert(0, initial_image_path)
        self._initial_image_paths = paths

        self._raw_text: str = ""
        self._images_data: list[tuple[bytes, str]] = []
        self.text_edit: QPlainTextEdit | None = None
        self.image_widget: ImagePicker | None = None
        self._setup_ui()
        if self.image_widget is not None and self._initial_image_paths:
            self.image_widget.set_image_paths(self._initial_image_paths)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Route Ctrl+V from the text field to the image area when clipboard has an image."""
        if (
            self.text_edit is not None
            and self.image_widget is not None
            and watched == self.text_edit
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_V
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
            and not QApplication.clipboard().image().isNull()
        ):
            self.image_widget.paste_image_from_clipboard()
            return True
        return super().eventFilter(watched, event)

    def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None:
        """Return the first image as bytes and MIME type, or `None`."""
        return self._images_data[0] if self._images_data else None

    def get_images_bytes_and_mime(self) -> list[tuple[bytes, str]]:
        """Return all provided images as `(bytes, mime)` pairs."""
        return list(self._images_data)

    def get_raw_text(self) -> str:
        """Return raw text entered by the user."""
        return self._raw_text

    def _is_input_valid(self, text: str, *, has_images: bool) -> bool:
        if self._text_required and not text:
            return False
        if self._images_required and not has_images:
            return False
        if self._text_required or self._images_required:
            return True
        # Default: at least one of text or images when both are shown.
        if self._show_text and self._show_images:
            return bool(text) or has_images
        if self._show_text:
            return bool(text)
        if self._show_images:
            return has_images
        return True

    def _on_accept(self) -> None:
        self._raw_text = self.text_edit.toPlainText().strip() if self.text_edit is not None else ""
        self._images_data = self.image_widget.get_images_bytes_and_mime() if self.image_widget is not None else []
        if not self._is_input_valid(self._raw_text, has_images=bool(self._images_data)):
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

        if self._show_text:
            self.text_edit = QPlainTextEdit()
            if self._placeholder:
                self.text_edit.setPlaceholderText(self._placeholder)
            self.text_edit.setMinimumHeight(120)
            self.text_edit.textChanged.connect(self._update_ok_enabled)
            self.text_edit.installEventFilter(self)
            layout.addWidget(self.text_edit)

        if self._show_images:
            if self._image_label:
                layout.addWidget(QLabel(self._image_label))
            self.image_widget = ImagePicker(
                mode=self._image_mode,
                max_image_side=self._max_image_side,
                fallback_text_edit=self.text_edit,
            )
            self.image_widget.image_changed.connect(self._update_ok_enabled)
            layout.addWidget(self.image_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if self._show_skip_manual:
            skip_button = make_emoji_push_button(self._skip_manual_button_text, "📝")
            skip_button.clicked.connect(self._on_skip_to_manual)
            button_layout.addWidget(skip_button)

        cancel_button = make_emoji_push_button("Cancel", "❌")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._ok_button = make_emoji_push_button(self._accept_button_text, self._accept_button_emoji)
        accept_font = QFont()
        accept_font.setBold(True)
        self._ok_button.setFont(accept_font)
        if self._accept_button_style:
            self._ok_button.setStyleSheet(self._accept_button_style)
        self._ok_button.setEnabled(False)
        self._ok_button.setDefault(True)
        self._ok_button.clicked.connect(self._on_accept)
        button_layout.addWidget(self._ok_button)

        layout.addLayout(button_layout)
        self._update_ok_enabled()

    def _update_ok_enabled(self) -> None:
        text = self.text_edit.toPlainText().strip() if self.text_edit is not None else ""
        has_image = self.image_widget.has_image() if self.image_widget is not None else False
        self._ok_button.setEnabled(self._is_input_valid(text, has_images=has_image))


# Backward-compatible alias used by older imports.
AiSourceDialog = TextImageSourceDialog
