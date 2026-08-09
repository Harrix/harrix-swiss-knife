---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_type_add_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseTypeAddDialog`](#%EF%B8%8F-class-exercisetypeadddialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_result`](#%EF%B8%8F-method-get_result)

</details>

## 🏛️ Class `ExerciseTypeAddDialog`

```python
class ExerciseTypeAddDialog(QDialog)
```

Modal dialog to enter a new exercise type or edit an existing one.

<details>
<summary>Code:</summary>

```python
class ExerciseTypeAddDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        exercises: list[str],
        selected_exercise: str = "",
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
        initial: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the add/edit exercise-type dialog.

        Args:

        - `initial` (`dict[str, Any] | None`): Existing type fields for edit mode
          (`exercise_name`, `type_name`, `calories_modifier`, `name_local`).

        """
        super().__init__(parent)
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._initial = initial or {}
        self._editing = bool(self._initial)
        self._result: tuple[str, str, float, str] | None = None

        self.setWindowTitle("Edit Exercise Type" if self._editing else "Add New Exercise Type")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form_group = QGroupBox("Exercise Type", self)
        form_layout = QVBoxLayout(form_group)

        exercise_row = QHBoxLayout()
        exercise_row.addWidget(QLabel("Exercise:", form_group))
        self._exercise_combo = QComboBox(form_group)
        self._exercise_combo.addItems(exercises)
        exercise_row.addWidget(self._exercise_combo, 1)
        form_layout.addLayout(exercise_row)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:", form_group))
        self._type_edit = QLineEdit(form_group)
        self._type_edit.setPlaceholderText("English type name")
        type_row.addWidget(self._type_edit, 1)
        form_layout.addLayout(type_row)

        name_local_row = QHBoxLayout()
        name_local_row.addWidget(QLabel("Local:", form_group))
        self._name_local_edit = QLineEdit(form_group)
        self._name_local_edit.setPlaceholderText("Local name")
        name_local_row.addWidget(self._name_local_edit, 1)
        self._translate_button = make_emoji_push_button("", "🤖")
        self._translate_button.setToolTip("Translate English → local, or local → English when Type is empty")
        self._translate_button.setFixedWidth(36)
        self._translate_button.clicked.connect(self._on_translate_clicked)
        name_local_row.addWidget(self._translate_button)
        form_layout.addLayout(name_local_row)

        modifier_row = QHBoxLayout()
        modifier_row.addWidget(QLabel("Calories modifier:", form_group))
        self._modifier_spin = QDoubleSpinBox(form_group)
        self._modifier_spin.setDecimals(1)
        self._modifier_spin.setMinimum(0.1)
        self._modifier_spin.setMaximum(10.0)
        self._modifier_spin.setValue(1.0)
        modifier_row.addWidget(self._modifier_spin, 1)
        form_layout.addLayout(modifier_row)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_initial(selected_exercise=selected_exercise)
        self._type_edit.setFocus()

    def get_result(self) -> tuple[str, str, float, str] | None:
        """Return `(exercise_name, type_name, calories_modifier, name_local)` or `None`."""
        return self._result

    def _on_accept(self) -> None:
        exercise = self._exercise_combo.currentText().strip()
        if not exercise:
            message_box.warning(self, "Validation Error", "Select an exercise")
            return
        type_name = self._type_edit.text().strip()
        if not type_name:
            message_box.warning(self, "Validation Error", "Enter type name")
            return
        self._result = (
            exercise,
            type_name,
            self._modifier_spin.value(),
            self._name_local_edit.text().strip(),
        )
        self.accept()

    def _on_translate_clicked(self) -> None:
        request_name_local_translation(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            name_edit=self._type_edit,
            name_local_edit=self._name_local_edit,
            translate_button=self._translate_button,
        )

    def _populate_initial(self, *, selected_exercise: str) -> None:
        exercise_to_select = str(self._initial.get("exercise_name") or selected_exercise or "")
        if exercise_to_select:
            index = self._exercise_combo.findText(exercise_to_select)
            if index >= 0:
                self._exercise_combo.setCurrentIndex(index)
        if not self._initial:
            return
        self._type_edit.setText(str(self._initial.get("type_name") or ""))
        self._name_local_edit.setText(str(self._initial.get("name_local") or ""))
        try:
            self._modifier_spin.setValue(float(self._initial.get("calories_modifier") or 1.0))
        except (TypeError, ValueError):
            self._modifier_spin.setValue(1.0)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, exercises: list[str], selected_exercise: str = '', app_config: dict[str, Any] | None = None, bothub_state: BothubRequestState | None = None, initial: dict[str, Any] | None = None) -> None
```

Initialize the add/edit exercise-type dialog.

Args:

- `initial` (`dict[str, Any] | None`): Existing type fields for edit mode
  (`exercise_name`, `type_name`, `calories_modifier`, `name_local`).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        exercises: list[str],
        selected_exercise: str = "",
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
        initial: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(parent)
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._initial = initial or {}
        self._editing = bool(self._initial)
        self._result: tuple[str, str, float, str] | None = None

        self.setWindowTitle("Edit Exercise Type" if self._editing else "Add New Exercise Type")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form_group = QGroupBox("Exercise Type", self)
        form_layout = QVBoxLayout(form_group)

        exercise_row = QHBoxLayout()
        exercise_row.addWidget(QLabel("Exercise:", form_group))
        self._exercise_combo = QComboBox(form_group)
        self._exercise_combo.addItems(exercises)
        exercise_row.addWidget(self._exercise_combo, 1)
        form_layout.addLayout(exercise_row)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:", form_group))
        self._type_edit = QLineEdit(form_group)
        self._type_edit.setPlaceholderText("English type name")
        type_row.addWidget(self._type_edit, 1)
        form_layout.addLayout(type_row)

        name_local_row = QHBoxLayout()
        name_local_row.addWidget(QLabel("Local:", form_group))
        self._name_local_edit = QLineEdit(form_group)
        self._name_local_edit.setPlaceholderText("Local name")
        name_local_row.addWidget(self._name_local_edit, 1)
        self._translate_button = make_emoji_push_button("", "🤖")
        self._translate_button.setToolTip("Translate English → local, or local → English when Type is empty")
        self._translate_button.setFixedWidth(36)
        self._translate_button.clicked.connect(self._on_translate_clicked)
        name_local_row.addWidget(self._translate_button)
        form_layout.addLayout(name_local_row)

        modifier_row = QHBoxLayout()
        modifier_row.addWidget(QLabel("Calories modifier:", form_group))
        self._modifier_spin = QDoubleSpinBox(form_group)
        self._modifier_spin.setDecimals(1)
        self._modifier_spin.setMinimum(0.1)
        self._modifier_spin.setMaximum(10.0)
        self._modifier_spin.setValue(1.0)
        modifier_row.addWidget(self._modifier_spin, 1)
        form_layout.addLayout(modifier_row)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_initial(selected_exercise=selected_exercise)
        self._type_edit.setFocus()
```

</details>

### ⚙️ Method `get_result`

```python
def get_result(self) -> tuple[str, str, float, str] | None
```

Return `(exercise_name, type_name, calories_modifier, name_local)` or `None`.

<details>
<summary>Code:</summary>

```python
def get_result(self) -> tuple[str, str, float, str] | None:
        return self._result
```

</details>
