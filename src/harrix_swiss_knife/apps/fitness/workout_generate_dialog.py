"""Dialog: gender, duration, and preferences before asking BotHub to generate a workout."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.fitness.workouts_ai import WorkoutGeneratePreferences
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons


class WorkoutGenerateDialog(QDialog):
    """Collect athlete gender, planned duration, and workout preferences."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        show_gender: bool = True,
        initial_gender: str | None = None,
        initial_duration_min: int | None = None,
    ) -> None:
        """Build the form with optional male/female choice and duration in minutes."""
        super().__init__(parent)
        self.setWindowTitle("New workout")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(420)
        self._fixed_gender: str | None = None
        if not show_gender:
            normalized = str(initial_gender or "").strip().lower()
            self._fixed_gender = normalized if normalized in {"male", "female"} else "male"

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.radio_male = QRadioButton("Male")
        self.radio_female = QRadioButton("Female")
        if show_gender:
            preselect = str(initial_gender or "").strip().lower()
            if preselect == "female":
                self.radio_female.setChecked(True)
            else:
                self.radio_male.setChecked(True)
            gender = QWidget()
            gender_layout = QVBoxLayout(gender)
            gender_layout.setContentsMargins(0, 0, 0, 0)
            gender_layout.addWidget(self.radio_male)
            gender_layout.addWidget(self.radio_female)
            form.addRow("Gender:", gender)

        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(10, 240)
        duration = 45 if initial_duration_min is None else int(initial_duration_min)
        self.spin_duration.setValue(max(10, min(duration, 240)))
        self.spin_duration.setSuffix(" min")
        form.addRow("Duration:", self.spin_duration)
        layout.addLayout(form)

        preferences = QGroupBox("Preferences")
        preferences_layout = QVBoxLayout(preferences)
        self.check_dumbbells = QCheckBox("Dumbbells")
        self.check_cardio = QCheckBox("Cardio")
        self.check_stretching = QCheckBox("Stretching")
        self.check_yoga = QCheckBox("Yoga")
        self.check_strength = QCheckBox("Strength")
        self.check_something_new = QCheckBox("Something new")
        for checkbox in (
            self.check_dumbbells,
            self.check_cardio,
            self.check_stretching,
            self.check_yoga,
            self.check_strength,
            self.check_something_new,
        ):
            preferences_layout.addWidget(checkbox)
        layout.addWidget(preferences)

        notes_form = QFormLayout()
        self.line_notes = QLineEdit()
        self.line_notes.setPlaceholderText("Optional notes, e.g. focus on back, no jumping")
        notes_form.addRow("Notes:", self.line_notes)
        layout.addLayout(notes_form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def duration_min(self) -> int:
        """Return planned duration in minutes."""
        return int(self.spin_duration.value())

    def gender(self) -> str:
        """Return `male` or `female`."""
        if self._fixed_gender is not None:
            return self._fixed_gender
        return "female" if self.radio_female.isChecked() else "male"

    def preferences(self) -> WorkoutGeneratePreferences:
        """Return selected workout focus areas and notes."""
        return WorkoutGeneratePreferences(
            dumbbells=self.check_dumbbells.isChecked(),
            cardio=self.check_cardio.isChecked(),
            stretching=self.check_stretching.isChecked(),
            yoga=self.check_yoga.isChecked(),
            strength=self.check_strength.isChecked(),
            try_something_new=self.check_something_new.isChecked(),
            notes=self.line_notes.text().strip(),
        )
