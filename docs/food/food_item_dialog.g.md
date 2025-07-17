---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_item_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodItemDialog`](#%EF%B8%8F-class-fooditemdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `accept`](#%EF%B8%8F-method-accept)
  - [⚙️ Method `delete_item`](#%EF%B8%8F-method-delete_item)
  - [⚙️ Method `get_edited_data`](#%EF%B8%8F-method-get_edited_data)
  - [⚙️ Method `setup_data`](#%EF%B8%8F-method-setup_data)
  - [⚙️ Method `setup_ui`](#%EF%B8%8F-method-setup_ui)

</details>

## 🏛️ Class `FoodItemDialog`

```python
class FoodItemDialog(QDialog)
```

Dialog for editing food item parameters.

<details>
<summary>Code:</summary>

```python
class FoodItemDialog(QDialog):

    def __init__(self, parent=None, food_item_data=None):
        """Initialize the dialog.

        Args:
            parent: Parent widget
            food_item_data: Food item data as [id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories]
        """
        super().__init__(parent)
        self.food_item_data = food_item_data
        self.setup_ui()
        self.setup_data()

    def accept(self):
        """Handle accept (save) button click."""
        # Validate required fields
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required!")
            return

        # Check if at least one of calories fields is filled
        calories_per_100g = self.calories_per_100g_spinbox.value()
        default_portion_calories = self.default_portion_calories_spinbox.value()

        if calories_per_100g == 0 and default_portion_calories == 0:
            QMessageBox.warning(
                self, "Validation Error", "Please fill either 'Calories per 100g' or 'Default Portion Calories'!"
            )
            return

        super().accept()

    def delete_item(self):
        """Handle delete button click."""
        if not self.food_item_data:
            return

        food_name = self.food_item_data[1] if self.food_item_data[1] else "this item"

        reply = QMessageBox.question(
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

    def get_edited_data(self):
        """Get the edited data as a dictionary."""
        return {
            "name": self.name_edit.text().strip(),
            "name_en": self.name_en_edit.text().strip() or None,
            "is_drink": self.is_drink_checkbox.isChecked(),
            "calories_per_100g": self.calories_per_100g_spinbox.value() or None,
            "default_portion_weight": self.default_portion_weight_spinbox.value() or None,
            "default_portion_calories": self.default_portion_calories_spinbox.value() or None,
        }

    def setup_data(self):
        """Setup initial data from food_item_data."""
        if self.food_item_data:
            # food_item_data format: [id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories]
            self.name_edit.setText(self.food_item_data[1] if self.food_item_data[1] else "")
            self.name_en_edit.setText(self.food_item_data[2] if self.food_item_data[2] else "")
            self.is_drink_checkbox.setChecked(self.food_item_data[3] == 1)
            self.calories_per_100g_spinbox.setValue(self.food_item_data[4] if self.food_item_data[4] else 0)
            self.default_portion_weight_spinbox.setValue(int(self.food_item_data[5]) if self.food_item_data[5] else 0)
            self.default_portion_calories_spinbox.setValue(self.food_item_data[6] if self.food_item_data[6] else 0)

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Edit Food Item")
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

        # Delete button
        self.delete_button = QPushButton("🗑️ Delete Item")
        self.delete_button.setStyleSheet("QPushButton { color: red; }")
        self.delete_button.clicked.connect(self.delete_item)
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()

        # Standard dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        button_layout.addWidget(self.button_box)

        layout.addLayout(button_layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent = None, food_item_data = None)
```

Initialize the dialog.

Args:
parent: Parent widget
food_item_data: Food item data as [id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories]

<details>
<summary>Code:</summary>

```python
def __init__(self, parent=None, food_item_data=None):
        super().__init__(parent)
        self.food_item_data = food_item_data
        self.setup_ui()
        self.setup_data()
```

</details>

### ⚙️ Method `accept`

```python
def accept(self)
```

Handle accept (save) button click.

<details>
<summary>Code:</summary>

```python
def accept(self):
        # Validate required fields
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required!")
            return

        # Check if at least one of calories fields is filled
        calories_per_100g = self.calories_per_100g_spinbox.value()
        default_portion_calories = self.default_portion_calories_spinbox.value()

        if calories_per_100g == 0 and default_portion_calories == 0:
            QMessageBox.warning(
                self, "Validation Error", "Please fill either 'Calories per 100g' or 'Default Portion Calories'!"
            )
            return

        super().accept()
```

</details>

### ⚙️ Method `delete_item`

```python
def delete_item(self)
```

Handle delete button click.

<details>
<summary>Code:</summary>

```python
def delete_item(self):
        if not self.food_item_data:
            return

        food_name = self.food_item_data[1] if self.food_item_data[1] else "this item"

        reply = QMessageBox.question(
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
```

</details>

### ⚙️ Method `get_edited_data`

```python
def get_edited_data(self)
```

Get the edited data as a dictionary.

<details>
<summary>Code:</summary>

```python
def get_edited_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "name_en": self.name_en_edit.text().strip() or None,
            "is_drink": self.is_drink_checkbox.isChecked(),
            "calories_per_100g": self.calories_per_100g_spinbox.value() or None,
            "default_portion_weight": self.default_portion_weight_spinbox.value() or None,
            "default_portion_calories": self.default_portion_calories_spinbox.value() or None,
        }
```

</details>

### ⚙️ Method `setup_data`

```python
def setup_data(self)
```

Setup initial data from food_item_data.

<details>
<summary>Code:</summary>

```python
def setup_data(self):
        if self.food_item_data:
            # food_item_data format: [id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories]
            self.name_edit.setText(self.food_item_data[1] if self.food_item_data[1] else "")
            self.name_en_edit.setText(self.food_item_data[2] if self.food_item_data[2] else "")
            self.is_drink_checkbox.setChecked(self.food_item_data[3] == 1)
            self.calories_per_100g_spinbox.setValue(self.food_item_data[4] if self.food_item_data[4] else 0)
            self.default_portion_weight_spinbox.setValue(int(self.food_item_data[5]) if self.food_item_data[5] else 0)
            self.default_portion_calories_spinbox.setValue(self.food_item_data[6] if self.food_item_data[6] else 0)
```

</details>

### ⚙️ Method `setup_ui`

```python
def setup_ui(self)
```

Setup the user interface.

<details>
<summary>Code:</summary>

```python
def setup_ui(self):
        self.setWindowTitle("Edit Food Item")
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

        # Delete button
        self.delete_button = QPushButton("🗑️ Delete Item")
        self.delete_button.setStyleSheet("QPushButton { color: red; }")
        self.delete_button.clicked.connect(self.delete_item)
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()

        # Standard dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        button_layout.addWidget(self.button_box)

        layout.addLayout(button_layout)
```

</details>
