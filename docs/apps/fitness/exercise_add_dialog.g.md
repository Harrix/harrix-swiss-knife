---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_add_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseAddDialog`](#%EF%B8%8F-class-exerciseadddialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_result`](#%EF%B8%8F-method-get_result)

</details>

## 🏛️ Class `ExerciseAddDialog`

```python
class ExerciseAddDialog(QDialog)
```

Modal dialog to enter a new exercise or edit an existing one.

<details>
<summary>Code:</summary>

```python
class ExerciseAddDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
        initial: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the add/edit exercise dialog.

        Args:

        - `initial` (`dict[str, Any] | None`): Existing exercise fields for edit mode
          (`name`, `unit`, `is_type_required`, `calories_per_unit`, `name_local`,
          `is_favorite`). Favorite is shown only when editing.

        """
        super().__init__(parent)
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._initial = initial or {}
        self._editing = bool(self._initial)
        self._result: tuple[str, str, bool, float, str, bool, str] | None = None

        self.setWindowTitle("Edit Exercise" if self._editing else "Add New Exercise")
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

        self._favorite_check: QCheckBox | None = None
        if self._editing:
            self._favorite_check = QCheckBox("Favorite", form_group)
            form_layout.addWidget(self._favorite_check)

        media_hint = (
            "Optional: drag and drop new video/image to replace media"
            if self._editing
            else "Drag and drop video/image (mp4, avif, gif, png, jpeg…)"
        )
        self._media_drop = FileDropWidget(
            form_group,
            name_filter=MEDIA_FILE_FILTER,
            allowed_extensions=EXERCISE_MEDIA_EXTENSIONS,
            hint_text=media_hint,
            dialog_title="Select exercise media",
            path_filter=is_exercise_media_path,
        )
        form_layout.addWidget(self._media_drop)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        self._fill_button = make_emoji_push_button("Fill with AI", "🤖")
        self._fill_button.setToolTip(
            "Fill English/local names, unit, and calories from the entered name or media filename",
        )
        self._fill_button.clicked.connect(self._on_fill_clicked)
        buttons.addButton(self._fill_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_initial()
        self._name_edit.setFocus()

    def get_result(self) -> tuple[str, str, bool, float, str, bool, str] | None:
        """Return `(name, unit, is_type_required, calories, name_local, is_favorite, media_path)` or `None`."""
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
            self._favorite_check.isChecked() if self._favorite_check is not None else False,
            self._media_drop.get_file_path(),
        )
        self.accept()

    def _on_fill_clicked(self) -> None:
        request_exercise_fill(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            name_edit=self._name_edit,
            name_local_edit=self._name_local_edit,
            unit_edit=self._unit_edit,
            calories_spin=self._calories_spin,
            fill_button=self._fill_button,
            media_path=self._media_drop.get_file_path(),
        )

    def _populate_initial(self) -> None:
        if not self._initial:
            return
        self._name_edit.setText(str(self._initial.get("name") or ""))
        self._name_local_edit.setText(str(self._initial.get("name_local") or ""))
        self._unit_edit.setText(str(self._initial.get("unit") or ""))
        try:
            self._calories_spin.setValue(float(self._initial.get("calories_per_unit") or 0.0))
        except (TypeError, ValueError):
            self._calories_spin.setValue(0.0)
        self._type_required_check.setChecked(bool(self._initial.get("is_type_required")))
        if self._favorite_check is not None:
            self._favorite_check.setChecked(bool(self._initial.get("is_favorite")))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, app_config: dict[str, Any] | None = None, bothub_state: BothubRequestState | None = None, initial: dict[str, Any] | None = None) -> None
```

Initialize the add/edit exercise dialog.

Args:

- `initial` (`dict[str, Any] | None`): Existing exercise fields for edit mode
  (`name`, `unit`, `is_type_required`, `calories_per_unit`, `name_local`,
  `is_favorite`). Favorite is shown only when editing.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
        initial: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(parent)
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._initial = initial or {}
        self._editing = bool(self._initial)
        self._result: tuple[str, str, bool, float, str, bool, str] | None = None

        self.setWindowTitle("Edit Exercise" if self._editing else "Add New Exercise")
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

        self._favorite_check: QCheckBox | None = None
        if self._editing:
            self._favorite_check = QCheckBox("Favorite", form_group)
            form_layout.addWidget(self._favorite_check)

        media_hint = (
            "Optional: drag and drop new video/image to replace media"
            if self._editing
            else "Drag and drop video/image (mp4, avif, gif, png, jpeg…)"
        )
        self._media_drop = FileDropWidget(
            form_group,
            name_filter=MEDIA_FILE_FILTER,
            allowed_extensions=EXERCISE_MEDIA_EXTENSIONS,
            hint_text=media_hint,
            dialog_title="Select exercise media",
            path_filter=is_exercise_media_path,
        )
        form_layout.addWidget(self._media_drop)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        self._fill_button = make_emoji_push_button("Fill with AI", "🤖")
        self._fill_button.setToolTip(
            "Fill English/local names, unit, and calories from the entered name or media filename",
        )
        self._fill_button.clicked.connect(self._on_fill_clicked)
        buttons.addButton(self._fill_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_initial()
        self._name_edit.setFocus()
```

</details>

### ⚙️ Method `get_result`

```python
def get_result(self) -> tuple[str, str, bool, float, str, bool, str] | None
```

Return `(name, unit, is_type_required, calories, name_local, is_favorite, media_path)` or `None`.

<details>
<summary>Code:</summary>

```python
def get_result(self) -> tuple[str, str, bool, float, str, bool, str] | None:
        return self._result
```

</details>
