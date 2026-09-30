---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `calorie_thresholds_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CalorieThresholdsSetupDialog`](#%EF%B8%8F-class-caloriethresholdssetupdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `result_profile`](#%EF%B8%8F-method-result_profile)
  - [⚙️ Method `result_thresholds`](#%EF%B8%8F-method-result_thresholds)

</details>

## 🏛️ Class `CalorieThresholdsSetupDialog`

```python
class CalorieThresholdsSetupDialog(QDialog)
```

Ask for body metrics, suggest bands, and let the user edit them.

<details>
<summary>Code:</summary>

```python
class CalorieThresholdsSetupDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        profile: PersonProfile | None = None,
        thresholds: CalorieThresholds | None = None,
    ) -> None:
        """Build the form; optional `profile` / `thresholds` pre-fill fields."""
        super().__init__(parent)
        self.setWindowTitle("Calorie thresholds")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(460)

        initial = profile or PersonProfile(sex="male", age=30, height_cm=175.0, weight_kg=70.0)
        self._syncing = False

        layout = QVBoxLayout(self)
        intro = QLabel(
            "Enter age, height, weight, sex, and activity. "
            "Daily calorie bands are estimated with Mifflin St Jeor (BMR x activity). "
            "You can adjust the three boundary values before saving.",
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self._sex = QComboBox()
        self._sex.addItem("Male", "male")
        self._sex.addItem("Female", "female")
        self._sex.setCurrentIndex(0 if initial.sex == "male" else 1)
        form.addRow("Sex:", self._sex)

        self._age = QSpinBox()
        self._age.setRange(10, 120)
        self._age.setValue(initial.age)
        self._age.setSuffix(" years")
        form.addRow("Age:", self._age)

        self._height = QDoubleSpinBox()
        self._height.setRange(100.0, 250.0)
        self._height.setDecimals(1)
        self._height.setSingleStep(0.5)
        self._height.setValue(initial.height_cm)
        self._height.setSuffix(" cm")
        form.addRow("Height:", self._height)

        self._weight = QDoubleSpinBox()
        self._weight.setRange(30.0, 300.0)
        self._weight.setDecimals(1)
        self._weight.setSingleStep(0.1)
        self._weight.setValue(initial.weight_kg)
        self._weight.setSuffix(" kg")
        form.addRow("Weight:", self._weight)

        self._activity = QComboBox()
        for level, label in ACTIVITY_LABELS:
            self._activity.addItem(label, level)
        activity_index = self._activity.findData(initial.activity)
        self._activity.setCurrentIndex(max(activity_index, 0))
        form.addRow("Activity:", self._activity)

        self._want_to_lose_weight = QCheckBox("I want to lose weight")
        self._want_to_lose_weight.setChecked(initial.want_to_lose_weight)
        self._want_to_lose_weight.setToolTip("Lowers all three calorie bands by about 15%.")
        form.addRow("", self._want_to_lose_weight)

        self._estimate_label = QLabel("")
        self._estimate_label.setWordWrap(True)
        form.addRow("Estimate:", self._estimate_label)

        self._low = QSpinBox()
        self._medium_low = QSpinBox()
        self._medium_high = QSpinBox()
        for spin in (self._low, self._medium_low, self._medium_high):
            spin.setRange(500, 10000)
            spin.setSingleStep(50)
            spin.setSuffix(" kcal")
        form.addRow("Low (<= green):", self._low)
        form.addRow("Medium-low (<= yellow):", self._medium_low)
        form.addRow("Medium-high (<= orange):", self._medium_high)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        )
        apply_lucide_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        for widget in (self._sex, self._age, self._height, self._weight, self._activity):
            if isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._recalculate)
            else:
                widget.valueChanged.connect(self._recalculate)
        self._want_to_lose_weight.toggled.connect(self._recalculate)

        self._recalculate()
        if thresholds is not None:
            self._set_threshold_spins(thresholds)

    def result_profile(self) -> PersonProfile:
        """Return the body-metrics profile from the form."""
        sex = self._sex.currentData()
        activity = self._activity.currentData()
        if activity not in ACTIVITY_FACTORS:
            activity = "moderate"
        return PersonProfile(
            sex=sex if sex in {"male", "female"} else "male",  # type: ignore[arg-type]
            age=int(self._age.value()),
            height_cm=float(self._height.value()),
            weight_kg=float(self._weight.value()),
            activity=activity,  # type: ignore[arg-type]
            want_to_lose_weight=self._want_to_lose_weight.isChecked(),
        )

    def result_thresholds(self) -> CalorieThresholds:
        """Return the (possibly edited) calorie bands."""
        low = int(self._low.value())
        medium_low = max(low, int(self._medium_low.value()))
        medium_high = max(medium_low, int(self._medium_high.value()))
        return CalorieThresholds(
            low=float(low),
            medium_low=float(medium_low),
            medium_high=float(medium_high),
        )

    def _recalculate(self) -> None:
        if self._syncing:
            return
        estimate = estimate_calorie_bands(self.result_profile())
        deficit_note = " · lose-weight -15%" if self._want_to_lose_weight.isChecked() else ""
        self._estimate_label.setText(
            f"BMR ~ {estimate.bmr:.0f} kcal/day · TDEE ~ {estimate.tdee:.0f} kcal/day{deficit_note}",
        )
        self._set_threshold_spins(estimate.thresholds)

    def _set_threshold_spins(self, thresholds: CalorieThresholds) -> None:
        self._syncing = True
        try:
            self._low.setValue(int(thresholds.low))
            self._medium_low.setValue(int(thresholds.medium_low))
            self._medium_high.setValue(int(thresholds.medium_high))
        finally:
            self._syncing = False
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, profile: PersonProfile | None = None, thresholds: CalorieThresholds | None = None) -> None
```

Build the form; optional `profile` / `thresholds` pre-fill fields.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        profile: PersonProfile | None = None,
        thresholds: CalorieThresholds | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Calorie thresholds")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(460)

        initial = profile or PersonProfile(sex="male", age=30, height_cm=175.0, weight_kg=70.0)
        self._syncing = False

        layout = QVBoxLayout(self)
        intro = QLabel(
            "Enter age, height, weight, sex, and activity. "
            "Daily calorie bands are estimated with Mifflin St Jeor (BMR x activity). "
            "You can adjust the three boundary values before saving.",
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self._sex = QComboBox()
        self._sex.addItem("Male", "male")
        self._sex.addItem("Female", "female")
        self._sex.setCurrentIndex(0 if initial.sex == "male" else 1)
        form.addRow("Sex:", self._sex)

        self._age = QSpinBox()
        self._age.setRange(10, 120)
        self._age.setValue(initial.age)
        self._age.setSuffix(" years")
        form.addRow("Age:", self._age)

        self._height = QDoubleSpinBox()
        self._height.setRange(100.0, 250.0)
        self._height.setDecimals(1)
        self._height.setSingleStep(0.5)
        self._height.setValue(initial.height_cm)
        self._height.setSuffix(" cm")
        form.addRow("Height:", self._height)

        self._weight = QDoubleSpinBox()
        self._weight.setRange(30.0, 300.0)
        self._weight.setDecimals(1)
        self._weight.setSingleStep(0.1)
        self._weight.setValue(initial.weight_kg)
        self._weight.setSuffix(" kg")
        form.addRow("Weight:", self._weight)

        self._activity = QComboBox()
        for level, label in ACTIVITY_LABELS:
            self._activity.addItem(label, level)
        activity_index = self._activity.findData(initial.activity)
        self._activity.setCurrentIndex(max(activity_index, 0))
        form.addRow("Activity:", self._activity)

        self._want_to_lose_weight = QCheckBox("I want to lose weight")
        self._want_to_lose_weight.setChecked(initial.want_to_lose_weight)
        self._want_to_lose_weight.setToolTip("Lowers all three calorie bands by about 15%.")
        form.addRow("", self._want_to_lose_weight)

        self._estimate_label = QLabel("")
        self._estimate_label.setWordWrap(True)
        form.addRow("Estimate:", self._estimate_label)

        self._low = QSpinBox()
        self._medium_low = QSpinBox()
        self._medium_high = QSpinBox()
        for spin in (self._low, self._medium_low, self._medium_high):
            spin.setRange(500, 10000)
            spin.setSingleStep(50)
            spin.setSuffix(" kcal")
        form.addRow("Low (<= green):", self._low)
        form.addRow("Medium-low (<= yellow):", self._medium_low)
        form.addRow("Medium-high (<= orange):", self._medium_high)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        )
        apply_lucide_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        for widget in (self._sex, self._age, self._height, self._weight, self._activity):
            if isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._recalculate)
            else:
                widget.valueChanged.connect(self._recalculate)
        self._want_to_lose_weight.toggled.connect(self._recalculate)

        self._recalculate()
        if thresholds is not None:
            self._set_threshold_spins(thresholds)
```

</details>

### ⚙️ Method `result_profile`

```python
def result_profile(self) -> PersonProfile
```

Return the body-metrics profile from the form.

<details>
<summary>Code:</summary>

```python
def result_profile(self) -> PersonProfile:
        sex = self._sex.currentData()
        activity = self._activity.currentData()
        if activity not in ACTIVITY_FACTORS:
            activity = "moderate"
        return PersonProfile(
            sex=sex if sex in {"male", "female"} else "male",  # type: ignore[arg-type]
            age=int(self._age.value()),
            height_cm=float(self._height.value()),
            weight_kg=float(self._weight.value()),
            activity=activity,  # type: ignore[arg-type]
            want_to_lose_weight=self._want_to_lose_weight.isChecked(),
        )
```

</details>

### ⚙️ Method `result_thresholds`

```python
def result_thresholds(self) -> CalorieThresholds
```

Return the (possibly edited) calorie bands.

<details>
<summary>Code:</summary>

```python
def result_thresholds(self) -> CalorieThresholds:
        low = int(self._low.value())
        medium_low = max(low, int(self._medium_low.value()))
        medium_high = max(medium_low, int(self._medium_high.value()))
        return CalorieThresholds(
            low=float(low),
            medium_low=float(medium_low),
            medium_high=float(medium_high),
        )
```

</details>
