---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `portion_calories_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PortionCaloriesDialog`](#%EF%B8%8F-class-portioncaloriesdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `calories_per_100g`](#%EF%B8%8F-method-calories_per_100g)
  - [⚙️ Method `food_name (property)`](#%EF%B8%8F-method-food_name-property)
  - [⚙️ Method `is_drink (property)`](#%EF%B8%8F-method-is_drink-property)
  - [⚙️ Method `is_drink (setter)`](#%EF%B8%8F-method-is_drink-setter)
  - [⚙️ Method `portion_calories`](#%EF%B8%8F-method-portion_calories)
  - [⚙️ Method `weight_g`](#%EF%B8%8F-method-weight_g)

</details>

## 🏛️ Class `PortionCaloriesDialog`

```python
class PortionCaloriesDialog(QDialog)
```

Collect weight and portion calories, then expose kcal/100g.

<details>
<summary>Code:</summary>

```python
class PortionCaloriesDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        *,
        food_name: str,
        initial_weight: int = 100,
        initial_portion_calories: float = 0,
        is_drink: bool = False,
        on_ai_weight: Callable[[PortionCaloriesDialog], None] | None = None,
    ) -> None:
        """Build the dialog; `on_ai_weight` is called when the AI button is pressed."""
        super().__init__(parent)
        self.setWindowTitle("Calories from portion")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(420)
        self._food_name = food_name.strip()
        self._is_drink = is_drink
        self._on_ai_weight = on_ai_weight

        layout = QVBoxLayout(self)
        if self._food_name:
            title = QLabel(self._food_name)
            title.setWordWrap(True)
            title.setStyleSheet("font-weight: bold;")
            layout.addWidget(title)

        form = QFormLayout()
        self.spin_weight = QSpinBox()
        self.spin_weight.setRange(1, 10000)
        self.spin_weight.setSuffix(" g")
        self.spin_weight.setValue(max(1, initial_weight))
        form.addRow("Weight:", self.spin_weight)

        self.spin_portion_calories = QDoubleSpinBox()
        self.spin_portion_calories.setRange(0, 10000)
        self.spin_portion_calories.setDecimals(1)
        self.spin_portion_calories.setSuffix(" kcal")
        self.spin_portion_calories.setValue(max(0.0, initial_portion_calories))
        form.addRow("Portion calories:", self.spin_portion_calories)

        self.label_per_100g = QLabel("")
        self.label_per_100g.setWordWrap(True)
        form.addRow("kcal / 100 g:", self.label_per_100g)
        layout.addLayout(form)

        self.spin_weight.valueChanged.connect(self._update_preview)
        self.spin_portion_calories.valueChanged.connect(self._update_preview)

        buttons = QHBoxLayout()
        self.button_ai = make_lucide_push_button("Determine weight with AI", "sparkles")
        self.button_ai.setToolTip(
            "Estimate portion weight from food name and portion calories",
        )
        self.button_ai.clicked.connect(self._emit_ai_weight)
        if on_ai_weight is None or not self._food_name:
            self.button_ai.setEnabled(False)
        buttons.addWidget(self.button_ai)
        buttons.addStretch(1)
        cancel = make_lucide_push_button("Cancel", CANCEL_BUTTON_ICON)
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        ok = make_lucide_push_button("Apply", OK_BUTTON_ICON)
        ok.setDefault(True)
        style_accept_button(ok)
        ok.clicked.connect(self.accept)
        buttons.addWidget(ok)
        layout.addLayout(buttons)

        self._update_preview()

    def calories_per_100g(self) -> float | None:
        """Return kcal/100g when weight and portion calories are valid."""
        weight = float(self.spin_weight.value())
        portion = float(self.spin_portion_calories.value())
        if weight <= 0 or portion <= 0:
            return None
        return convert_portion_to_calories_per_100g(weight=weight, portion_calories=portion)

    @property
    def food_name(self) -> str:
        """Food name shown in the dialog (used by AI lookup)."""
        return self._food_name

    @property
    def is_drink(self) -> bool:
        """Drink flag passed from the parent form (AI may update it)."""
        return self._is_drink

    @is_drink.setter
    def is_drink(self, value: bool) -> None:
        self._is_drink = bool(value)

    def portion_calories(self) -> float:
        """Portion energy entered by the user."""
        return float(self.spin_portion_calories.value())

    def weight_g(self) -> int:
        """Portion weight in grams."""
        return int(self.spin_weight.value())

    def _emit_ai_weight(self) -> None:
        if self._on_ai_weight is not None:
            self._on_ai_weight(self)

    def _update_preview(self) -> None:
        value = self.calories_per_100g()
        if value is None:
            self.label_per_100g.setText("—")
            return
        self.label_per_100g.setText(f"{value:.1f}")
        self.label_per_100g.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, *, food_name: str, initial_weight: int = 100, initial_portion_calories: float = 0, is_drink: bool = False, on_ai_weight: Callable[[PortionCaloriesDialog], None] | None = None) -> None
```

Build the dialog; `on_ai_weight` is called when the AI button is pressed.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        *,
        food_name: str,
        initial_weight: int = 100,
        initial_portion_calories: float = 0,
        is_drink: bool = False,
        on_ai_weight: Callable[[PortionCaloriesDialog], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Calories from portion")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(420)
        self._food_name = food_name.strip()
        self._is_drink = is_drink
        self._on_ai_weight = on_ai_weight

        layout = QVBoxLayout(self)
        if self._food_name:
            title = QLabel(self._food_name)
            title.setWordWrap(True)
            title.setStyleSheet("font-weight: bold;")
            layout.addWidget(title)

        form = QFormLayout()
        self.spin_weight = QSpinBox()
        self.spin_weight.setRange(1, 10000)
        self.spin_weight.setSuffix(" g")
        self.spin_weight.setValue(max(1, initial_weight))
        form.addRow("Weight:", self.spin_weight)

        self.spin_portion_calories = QDoubleSpinBox()
        self.spin_portion_calories.setRange(0, 10000)
        self.spin_portion_calories.setDecimals(1)
        self.spin_portion_calories.setSuffix(" kcal")
        self.spin_portion_calories.setValue(max(0.0, initial_portion_calories))
        form.addRow("Portion calories:", self.spin_portion_calories)

        self.label_per_100g = QLabel("")
        self.label_per_100g.setWordWrap(True)
        form.addRow("kcal / 100 g:", self.label_per_100g)
        layout.addLayout(form)

        self.spin_weight.valueChanged.connect(self._update_preview)
        self.spin_portion_calories.valueChanged.connect(self._update_preview)

        buttons = QHBoxLayout()
        self.button_ai = make_lucide_push_button("Determine weight with AI", "sparkles")
        self.button_ai.setToolTip(
            "Estimate portion weight from food name and portion calories",
        )
        self.button_ai.clicked.connect(self._emit_ai_weight)
        if on_ai_weight is None or not self._food_name:
            self.button_ai.setEnabled(False)
        buttons.addWidget(self.button_ai)
        buttons.addStretch(1)
        cancel = make_lucide_push_button("Cancel", CANCEL_BUTTON_ICON)
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        ok = make_lucide_push_button("Apply", OK_BUTTON_ICON)
        ok.setDefault(True)
        style_accept_button(ok)
        ok.clicked.connect(self.accept)
        buttons.addWidget(ok)
        layout.addLayout(buttons)

        self._update_preview()
```

</details>

### ⚙️ Method `calories_per_100g`

```python
def calories_per_100g(self) -> float | None
```

Return kcal/100g when weight and portion calories are valid.

<details>
<summary>Code:</summary>

```python
def calories_per_100g(self) -> float | None:
        weight = float(self.spin_weight.value())
        portion = float(self.spin_portion_calories.value())
        if weight <= 0 or portion <= 0:
            return None
        return convert_portion_to_calories_per_100g(weight=weight, portion_calories=portion)
```

</details>

### ⚙️ Method `food_name (property)`

```python
def food_name(self) -> str
```

Food name shown in the dialog (used by AI lookup).

<details>
<summary>Code:</summary>

```python
def food_name(self) -> str:
        return self._food_name
```

</details>

### ⚙️ Method `is_drink (property)`

```python
def is_drink(self) -> bool
```

Drink flag passed from the parent form (AI may update it).

<details>
<summary>Code:</summary>

```python
def is_drink(self) -> bool:
        return self._is_drink
```

</details>

### ⚙️ Method `is_drink (setter)`

```python
def is_drink(self, value: bool) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def is_drink(self, value: bool) -> None:
        self._is_drink = bool(value)
```

</details>

### ⚙️ Method `portion_calories`

```python
def portion_calories(self) -> float
```

Portion energy entered by the user.

<details>
<summary>Code:</summary>

```python
def portion_calories(self) -> float:
        return float(self.spin_portion_calories.value())
```

</details>

### ⚙️ Method `weight_g`

```python
def weight_g(self) -> int
```

Portion weight in grams.

<details>
<summary>Code:</summary>

```python
def weight_g(self) -> int:
        return int(self.spin_weight.value())
```

</details>
