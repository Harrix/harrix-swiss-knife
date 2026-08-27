"""Preview generated workout rows before saving."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.fitness.sets_ai import ParsedSetRow
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons


class WorkoutPreviewDialog(QDialog):
    """Editable title and set table for a generated workout."""

    def __init__(
        self,
        title: str,
        rows: list[ParsedSetRow],
        parent: QWidget | None = None,
    ) -> None:
        """Show `rows` in a table the user can edit before Save."""
        super().__init__(parent)
        self.setWindowTitle("Save workout")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumSize(560, 360)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.line_title = QLineEdit(title)
        self.line_title.setPlaceholderText("Workout name")
        form.addRow("Name:", self.line_title)
        layout.addLayout(form)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Exercise", "Type", "Value"])
        for row in rows:
            index = self.table.rowCount()
            self.table.insertRow(index)
            self.table.setItem(index, 0, QTableWidgetItem(row.exercise))
            self.table.setItem(index, 1, QTableWidgetItem(row.type_name))
            self.table.setItem(index, 2, QTableWidgetItem(row.value))
        self.table.resizeColumnsToContents()
        layout.addWidget(self.table, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def rows(self) -> list[ParsedSetRow]:
        """Return edited table rows."""
        result: list[ParsedSetRow] = []
        for index in range(self.table.rowCount()):
            exercise_item = self.table.item(index, 0)
            type_item = self.table.item(index, 1)
            value_item = self.table.item(index, 2)
            exercise = exercise_item.text().strip() if exercise_item else ""
            type_name = type_item.text().strip() if type_item else ""
            value = value_item.text().strip() if value_item else ""
            if exercise and value:
                result.append(ParsedSetRow(exercise=exercise, type_name=type_name, value=value))
        return result

    def title_text(self) -> str:
        """Return the workout name from the form."""
        return self.line_title.text().strip()
