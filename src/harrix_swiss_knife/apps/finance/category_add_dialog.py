"""Dialog for adding a new finance category."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.finance.category_name_ru_translate import request_category_name_ru_translation
from harrix_swiss_knife.integrations.bothub import BothubRequestState
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons, make_emoji_push_button


class CategoryAddDialog(QDialog):
    """Modal dialog to enter category name, Russian name, and type."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
    ) -> None:
        """Initialize the add-category dialog."""
        super().__init__(parent)
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._result: tuple[str, int, str] | None = None

        self.setWindowTitle("Add Category")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        form_group = QGroupBox("Category", self)
        form_layout = QVBoxLayout(form_group)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:", form_group))
        self._name_edit = QLineEdit(form_group)
        self._name_edit.setPlaceholderText("Category name")
        name_row.addWidget(self._name_edit, 1)
        form_layout.addLayout(name_row)

        name_ru_row = QHBoxLayout()
        name_ru_row.addWidget(QLabel("Russian:", form_group))
        self._name_ru_edit = QLineEdit(form_group)
        self._name_ru_edit.setPlaceholderText("Russian name")
        name_ru_row.addWidget(self._name_ru_edit, 1)
        self._translate_button = make_emoji_push_button("", "🤖")
        self._translate_button.setToolTip("Translate name to Russian with AI")
        self._translate_button.setFixedWidth(36)
        self._translate_button.clicked.connect(self._on_translate_clicked)
        name_ru_row.addWidget(self._translate_button)
        form_layout.addLayout(name_ru_row)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:", form_group))
        self._type_combo = QComboBox(form_group)
        self._type_combo.addItems(["Expense", "Income"])
        type_row.addWidget(self._type_combo, 1)
        form_layout.addLayout(type_row)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._name_edit.setFocus()

    def get_result(self) -> tuple[str, int, str] | None:
        """Return `(name, category_type, name_ru)` when accepted, else `None`."""
        return self._result

    def _on_accept(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            message_box.warning(self, "Validation Error", "Enter category name")
            return
        self._result = (name, self._type_combo.currentIndex(), self._name_ru_edit.text().strip())
        self.accept()

    def _on_translate_clicked(self) -> None:
        request_category_name_ru_translation(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            name_edit=self._name_edit,
            name_ru_edit=self._name_ru_edit,
            translate_button=self._translate_button,
        )
