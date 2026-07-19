"""Food item edit dialog.

This module contains a dialog for editing food items with all their parameters.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.food.database_manager import FoodItemByNameRow, FoodLogItemByNameRow
from harrix_swiss_knife.qt_emoji_icon import DELETE_BUTTON_EMOJI, apply_emoji_dialog_buttons, make_emoji_push_button


class FoodItemDialog(QDialog):
    """Dialog for editing or creating food item parameters.

    Attributes:

    - `food_item_data` (`FoodItemByNameRow | FoodLogItemByNameRow | None`): Source row for the form.
    - `is_create` (`bool`): When `True`, dialog creates a new food item (no delete).
    - `name_edit` (`QLineEdit`): Name input field.
    - `name_en_edit` (`QLineEdit`): English name input field.
    - `is_drink_checkbox` (`QCheckBox`): Checkbox for drink indicator.
    - `calories_per_100g_spinbox` (`QDoubleSpinBox`): Spinbox for calories per 100g.
    - `default_portion_weight_spinbox` (`QSpinBox`): Spinbox for default portion weight.
    - `default_portion_calories_spinbox` (`QDoubleSpinBox`): Spinbox for default portion calories.
    - `delete_button` (`QPushButton`): Button to delete the item.
    - `button_box` (`QDialogButtonBox`): Dialog button box with Save/Cancel.
    - `delete_confirmed` (`bool`): Flag indicating if deletion was confirmed.

    """

    food_item_data: FoodItemByNameRow | FoodLogItemByNameRow | None
    is_create: bool
    name_edit: QLineEdit
    name_en_edit: QLineEdit
    is_drink_checkbox: QCheckBox
    calories_per_100g_spinbox: QDoubleSpinBox
    default_portion_weight_spinbox: QSpinBox
    default_portion_calories_spinbox: QDoubleSpinBox
    delete_button: QPushButton
    button_box: QDialogButtonBox
    delete_confirmed: bool

    def __init__(
        self,
        parent: QWidget | None = None,
        food_item_data: FoodItemByNameRow | FoodLogItemByNameRow | None = None,
        *,
        is_create: bool = False,
    ) -> None:
        """Initialize the dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `food_item_data` (`FoodItemByNameRow | FoodLogItemByNameRow | None`): Row used to prefill
        the form. For create mode, may be `FoodLogItemByNameRow` from the latest log entry.
        - `is_create` (`bool`): When `True`, dialog is for creating a new food item. Defaults to `False`.

        """
        super().__init__(parent)
        self.food_item_data = food_item_data
        self.is_create = is_create
        self.delete_confirmed = False
        self.setup_ui()
        self.setup_data()

    def accept(self) -> None:
        """Handle accept (save) button click."""
        # Validate required fields
        name = self.name_edit.text().strip()
        if not name:
            message_box.warning(self, "Validation Error", "Name is required!")
            return

        # Check if at least one of calories fields is filled
        calories_per_100g = self.calories_per_100g_spinbox.value()
        default_portion_calories = self.default_portion_calories_spinbox.value()

        if calories_per_100g == 0 and default_portion_calories == 0:
            message_box.warning(
                self, "Validation Error", "Please fill either 'Calories per 100g' or 'Default Portion Calories'!"
            )
            return

        super().accept()

    def delete_item(self) -> None:
        """Handle delete button click."""
        if self.is_create or not isinstance(self.food_item_data, FoodItemByNameRow):
            return

        food_name = self.food_item_data.name or "this item"

        reply = message_box.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{food_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_confirmed = True
            self.accept()
        else:
            self.delete_confirmed = False

    def get_edited_data(self) -> dict:
        """Get the edited data as a dictionary.

        Returns:

        - `dict`: Dictionary containing the edited food item data.

        """
        return {
            "name": self.name_edit.text().strip(),
            "name_en": self.name_en_edit.text().strip() or None,
            "is_drink": self.is_drink_checkbox.isChecked(),
            "calories_per_100g": self.calories_per_100g_spinbox.value() or None,
            "default_portion_weight": self.default_portion_weight_spinbox.value() or None,
            "default_portion_calories": self.default_portion_calories_spinbox.value() or None,
        }

    def setup_data(self) -> None:
        """Set up initial data from food_item_data."""
        if not self.food_item_data:
            return

        if isinstance(self.food_item_data, FoodItemByNameRow):
            row = self.food_item_data
            name = row.name
            name_en = row.name_en
            is_drink = row.is_drink
            calories_per_100g = row.calories_per_100g
            default_portion_weight = row.default_portion_weight
            default_portion_calories = row.default_portion_calories
        else:
            row = self.food_item_data
            name = row.name or ""
            name_en = row.name_en
            is_drink = row.is_drink
            calories_per_100g = row.calories_per_100g
            default_portion_weight = row.weight
            default_portion_calories = row.portion_calories

        self.name_edit.setText(name or "")
        self.name_en_edit.setText(name_en or "")
        self.is_drink_checkbox.setChecked(is_drink)
        self.calories_per_100g_spinbox.setValue(calories_per_100g or 0)
        self.default_portion_weight_spinbox.setValue(int(default_portion_weight) if default_portion_weight else 0)
        self.default_portion_calories_spinbox.setValue(default_portion_calories or 0)

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Create Food Item" if self.is_create else "Edit Food Item")
        self.setModal(True)
        self.resize(400, 300)

        # Main layout
        layout = QVBoxLayout(self)

        # Form layout for input fields
        form_layout = QFormLayout()

        # Name field
        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)

        # English name field
        self.name_en_edit = QLineEdit()
        form_layout.addRow("English Name:", self.name_en_edit)

        # Is drink checkbox
        self.is_drink_checkbox = QCheckBox("Is Drink")
        form_layout.addRow("", self.is_drink_checkbox)

        # Calories per 100g field
        self.calories_per_100g_spinbox = QDoubleSpinBox()
        self.calories_per_100g_spinbox.setRange(0, 10000)
        self.calories_per_100g_spinbox.setDecimals(1)
        self.calories_per_100g_spinbox.setSuffix(" kcal/100g")
        form_layout.addRow("Calories per 100g:", self.calories_per_100g_spinbox)

        # Default portion weight field
        self.default_portion_weight_spinbox = QSpinBox()
        self.default_portion_weight_spinbox.setRange(0, 10000)
        self.default_portion_weight_spinbox.setSuffix(" g")
        form_layout.addRow("Default Portion Weight:", self.default_portion_weight_spinbox)

        # Default portion calories field
        self.default_portion_calories_spinbox = QDoubleSpinBox()
        self.default_portion_calories_spinbox.setRange(0, 10000)
        self.default_portion_calories_spinbox.setDecimals(1)
        self.default_portion_calories_spinbox.setSuffix(" kcal")
        form_layout.addRow("Default Portion Calories:", self.default_portion_calories_spinbox)

        layout.addLayout(form_layout)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Delete button (edit mode only)
        self.delete_button = make_emoji_push_button("Delete Item", DELETE_BUTTON_EMOJI)
        self.delete_button.setStyleSheet("QPushButton { color: red; }")
        self.delete_button.clicked.connect(self.delete_item)
        if self.is_create:
            self.delete_button.setVisible(False)
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()

        # Standard dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        apply_emoji_dialog_buttons(self.button_box)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        button_layout.addWidget(self.button_box)

        layout.addLayout(button_layout)
