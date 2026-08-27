"""Dialog: gender and duration before asking BotHub to generate a workout."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons


class WorkoutGenerateDialog(QDialog):
    """Collect athlete gender and planned duration."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the form with male/female and duration in minutes."""
        super().__init__(parent)
        self.setWindowTitle("New workout")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.radio_male = QRadioButton("Male")
        self.radio_female = QRadioButton("Female")
        self.radio_male.setChecked(True)
        gender = QWidget()
        gender_layout = QVBoxLayout(gender)
        gender_layout.setContentsMargins(0, 0, 0, 0)
        gender_layout.addWidget(self.radio_male)
        gender_layout.addWidget(self.radio_female)
        form.addRow("Gender:", gender)

        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(10, 240)
        self.spin_duration.setValue(45)
        self.spin_duration.setSuffix(" min")
        form.addRow("Duration:", self.spin_duration)
        layout.addLayout(form)

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
        return "female" if self.radio_female.isChecked() else "male"
