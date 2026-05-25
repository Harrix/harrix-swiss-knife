"""Preview BotHub prompt before sending a request."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


class BotHubPromptPreviewDialog(QDialog):
    """Show the full prompt and send to BotHub only after user confirmation."""

    def __init__(
        self,
        parent: QWidget | None,
        prompt_text: str,
        summary: str,
    ) -> None:
        """Initialize the prompt preview dialog.

        Args:

        - `parent` (`QWidget | None`): Parent window.
        - `prompt_text` (`str`): Full prompt that will be sent to BotHub.
        - `summary` (`str`): Short description of what will be requested.

        """
        super().__init__(parent)
        self.setWindowTitle("Translate with AI — prompt preview")
        self.resize(720, 520)

        layout = QVBoxLayout(self)

        summary_label = QLabel(summary, self)
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)

        prompt_label = QLabel("Prompt to send:", self)
        layout.addWidget(prompt_label)

        self._prompt_edit = QPlainTextEdit(self)
        self._prompt_edit.setPlainText(prompt_text)
        self._prompt_edit.setReadOnly(True)
        layout.addWidget(self._prompt_edit)

        button_box = QDialogButtonBox(self)
        send_button = button_box.addButton("Send to BotHub", QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        send_button.setDefault(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
