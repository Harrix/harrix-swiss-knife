---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `workout_generate_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `WorkoutGenerateDialog`](#%EF%B8%8F-class-workoutgeneratedialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `duration_min`](#%EF%B8%8F-method-duration_min)
  - [⚙️ Method `gender`](#%EF%B8%8F-method-gender)

</details>

## 🏛️ Class `WorkoutGenerateDialog`

```python
class WorkoutGenerateDialog(QDialog)
```

Collect athlete gender and planned duration.

<details>
<summary>Code:</summary>

```python
class WorkoutGenerateDialog(QDialog):

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the form with male/female and duration in minutes.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
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
```

</details>

### ⚙️ Method `duration_min`

```python
def duration_min(self) -> int
```

Return planned duration in minutes.

<details>
<summary>Code:</summary>

```python
def duration_min(self) -> int:
        return int(self.spin_duration.value())
```

</details>

### ⚙️ Method `gender`

```python
def gender(self) -> str
```

Return `male` or `female`.

<details>
<summary>Code:</summary>

```python
def gender(self) -> str:
        return "female" if self.radio_female.isChecked() else "male"
```

</details>
