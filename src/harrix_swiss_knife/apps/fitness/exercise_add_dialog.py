"""Dialog for adding a new fitness exercise."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.exercise_media import (
    EXERCISE_MEDIA_EXTENSIONS,
    MEDIA_FILE_FILTER,
    is_exercise_media_path,
)
from harrix_swiss_knife.apps.common.widgets.file_drop_widget import FileDropWidget
from harrix_swiss_knife.apps.fitness.name_local_translate import request_name_local_translation
from harrix_swiss_knife.integrations.bothub import BothubRequestState
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons, make_emoji_push_button


class ExerciseAddDialog(QDialog):
    """Modal dialog to enter a new exercise and optional media."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
    ) -> None:
        """Initialize the add-exercise dialog."""
        super().__init__(parent)
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._result: tuple[str, str, bool, float, str, str] | None = None

        self.setWindowTitle("Add New Exercise")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        form_group = QGroupBox("Exercise", self)
        form_layout = QVBoxLayout(form_group)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:", form_group))
        self._name_edit = QLineEdit(form_group)
        self._name_edit.setPlaceholderText("English name")
        name_row.addWidget(self._name_edit, 1)
        form_layout.addLayout(name_row)

        name_local_row = QHBoxLayout()
        name_local_row.addWidget(QLabel("Local:", form_group))
        self._name_local_edit = QLineEdit(form_group)
        self._name_local_edit.setPlaceholderText("Local name")
        name_local_row.addWidget(self._name_local_edit, 1)
        self._translate_button = make_emoji_push_button("", "🤖")
        self._translate_button.setToolTip("Translate English → local, or local → English when Name is empty")
        self._translate_button.setFixedWidth(36)
        self._translate_button.clicked.connect(self._on_translate_clicked)
        name_local_row.addWidget(self._translate_button)
        form_layout.addLayout(name_local_row)

        unit_row = QHBoxLayout()
        unit_row.addWidget(QLabel("Unit:", form_group))
        self._unit_edit = QLineEdit(form_group)
        self._unit_edit.setPlaceholderText("times, kg, m…")
        unit_row.addWidget(self._unit_edit, 1)
        form_layout.addLayout(unit_row)

        calories_row = QHBoxLayout()
        calories_row.addWidget(QLabel("Calories per unit:", form_group))
        self._calories_spin = QDoubleSpinBox(form_group)
        self._calories_spin.setDecimals(1)
        self._calories_spin.setMinimum(0.0)
        self._calories_spin.setMaximum(999.9)
        self._calories_spin.setValue(0.0)
        calories_row.addWidget(self._calories_spin, 1)
        form_layout.addLayout(calories_row)

        self._type_required_check = QCheckBox("Type is required", form_group)
        form_layout.addWidget(self._type_required_check)

        self._media_drop = FileDropWidget(
            form_group,
            name_filter=MEDIA_FILE_FILTER,
            allowed_extensions=EXERCISE_MEDIA_EXTENSIONS,
            hint_text="Drag and drop video/image (mp4, avif, gif, png, jpeg…)",
            dialog_title="Select exercise media",
            path_filter=is_exercise_media_path,
        )
        form_layout.addWidget(self._media_drop)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._name_edit.setFocus()

    def get_result(self) -> tuple[str, str, bool, float, str, str] | None:
        """Return `(name, unit, is_type_required, calories, name_local, media_path)` or `None`."""
        return self._result

    def _on_accept(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            message_box.warning(self, "Validation Error", "Enter exercise name")
            return
        self._result = (
            name,
            self._unit_edit.text().strip(),
            self._type_required_check.isChecked(),
            self._calories_spin.value(),
            self._name_local_edit.text().strip(),
            self._media_drop.get_file_path(),
        )
        self.accept()

    def _on_translate_clicked(self) -> None:
        request_name_local_translation(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            name_edit=self._name_edit,
            name_local_edit=self._name_local_edit,
            translate_button=self._translate_button,
        )
