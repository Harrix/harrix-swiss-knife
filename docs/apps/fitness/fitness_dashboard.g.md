---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fitness_dashboard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FitnessDashboardExercise`](#%EF%B8%8F-class-fitnessdashboardexercise)
- [🏛️ Class `FitnessDashboardWidget`](#%EF%B8%8F-class-fitnessdashboardwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `focus_value`](#%EF%B8%8F-method-focus_value)
  - [⚙️ Method `selected_exercise`](#%EF%B8%8F-method-selected_exercise)
  - [⚙️ Method `selected_type`](#%EF%B8%8F-method-selected_type)
  - [⚙️ Method `set_exercises`](#%EF%B8%8F-method-set_exercises)
  - [⚙️ Method `set_today_sets`](#%EF%B8%8F-method-set_today_sets)
  - [⚙️ Method `set_types`](#%EF%B8%8F-method-set_types)
  - [⚙️ Method `set_unit`](#%EF%B8%8F-method-set_unit)
  - [⚙️ Method `set_value`](#%EF%B8%8F-method-set_value)
  - [⚙️ Method `value`](#%EF%B8%8F-method-value)
- [🔧 Function `format_today_sets`](#-function-format_today_sets)
- [🔧 Function `make_circular_icon`](#-function-make_circular_icon)

</details>

## 🏛️ Class `FitnessDashboardExercise`

```python
class FitnessDashboardExercise
```

One exercise row on the Fitness dashboard list.

<details>
<summary>Code:</summary>

```python
class FitnessDashboardExercise:

    name: str
    name_local: str = ""
    icon: QIcon | None = None
```

</details>

## 🏛️ Class `FitnessDashboardWidget`

```python
class FitnessDashboardWidget(QWidget)
```

Quick-add card: circular exercise list, large value field, and today's sets.

<details>
<summary>Code:</summary>

```python
class FitnessDashboardWidget(QWidget):

    add_requested = Signal()
    exercise_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("FitnessDashboardWidget { background: #FFFFFF; }")
        self._model = QStandardItemModel(self)
        self._build_ui()

    def focus_value(self) -> None:
        """Move keyboard focus to the value field and select its text."""
        self._value_spin.setFocus()
        self._value_spin.selectAll()

    def selected_exercise(self) -> str:
        """Return the selected exercise name, or an empty string."""
        index = self._list.currentIndex()
        if not index.isValid():
            return ""
        name = index.data(Qt.ItemDataRole.UserRole)
        return str(name) if name else ""

    def selected_type(self) -> str:
        """Return the selected exercise type, or an empty string."""
        return self._type_combo.currentText().strip()

    def set_exercises(
        self,
        items: list[FitnessDashboardExercise],
        *,
        selected: str | None = None,
    ) -> None:
        """Replace the exercise list and optionally restore a selection.

        Args:

        - `items` (`list[FitnessDashboardExercise]`): Exercises to show.
        - `selected` (`str | None`): Exercise name to keep selected.

        """
        previous = selected if selected is not None else self.selected_exercise()
        self._list.blockSignals(True)  # noqa: FBT003
        self._model.clear()
        selected_row = 0
        for row, item in enumerate(items):
            letter = item.name[:1] if item.name else ""
            icon = make_circular_icon(item.icon, _DASHBOARD_ICON_SIZE, letter=letter)
            row_item = QStandardItem(item.name)
            row_item.setIcon(icon)
            row_item.setEditable(False)
            row_item.setData(item.name, Qt.ItemDataRole.UserRole)
            if item.name_local.strip():
                row_item.setData(item.name_local.strip(), NAME_LOCAL_ROLE)
            row_item.setSizeHint(QSize(0, _DASHBOARD_ICON_SIZE + 16))
            self._model.appendRow(row_item)
            if previous and item.name == previous:
                selected_row = row
        if self._model.rowCount() > 0:
            self._list.setCurrentIndex(self._model.index(selected_row, 0))
        self._list.blockSignals(False)  # noqa: FBT003
        self._on_exercise_index_changed(self._list.currentIndex())

    def set_today_sets(self, count: int) -> None:
        """Update the large sets figure shown under the add controls.

        Args:

        - `count` (`int`): Number of process records logged today.

        """
        self._sets_value.setText(format_today_sets(count))

    def set_types(self, types: list[str], *, selected: str = "") -> None:
        """Fill the type combo and show it only when types exist.

        Args:

        - `types` (`list[str]`): Type names for the selected exercise.
        - `selected` (`str`): Type to preselect when present.

        """
        self._type_combo.blockSignals(True)  # noqa: FBT003
        self._type_combo.clear()
        self._type_combo.addItem("")
        self._type_combo.addItems(types)
        if selected:
            index = self._type_combo.findText(selected)
            if index >= 0:
                self._type_combo.setCurrentIndex(index)
        self._type_combo.blockSignals(False)  # noqa: FBT003
        self._type_combo.setVisible(bool(types))

    def set_unit(self, unit: str) -> None:
        """Show the unit of the selected exercise under the value field.

        Args:

        - `unit` (`str`): Unit of measurement, or empty when nothing is selected.

        """
        text = unit.strip()
        self._unit_label.setText(text)
        self._unit_label.setVisible(bool(text))

    def set_value(self, value: int) -> None:
        """Set the numeric value used for the next set.

        Args:

        - `value` (`int`): Count, weight, or other exercise quantity.

        """
        self._value_spin.setValue(max(0, min(value, _VALUE_MAXIMUM)))

    def value(self) -> int:
        """Return the numeric value entered for the next set."""
        return int(self._value_spin.value())

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        pane = QFrame()
        pane.setObjectName("fitnessDashPane")
        pane.setStyleSheet(_PANE_STYLE)
        row = QHBoxLayout(pane)
        row.setContentsMargins(16, 16, 16, 16)
        row.setSpacing(24)

        self._list = QListView()
        self._list.setObjectName("fitnessDashExerciseList")
        self._list.setModel(self._model)
        self._list.setIconSize(QSize(_DASHBOARD_ICON_SIZE, _DASHBOARD_ICON_SIZE))
        self._list.setItemDelegate(NameLocalListDelegate(self._list, layout=NameLocalLayout.LIST))
        self._list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self._list.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self._list.setUniformItemSizes(True)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setMinimumWidth(300)
        self._list.setStyleSheet(_LIST_STYLE)
        self._list.selectionModel().currentChanged.connect(self._on_exercise_index_changed)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(8, 8, 8, 8)
        center_layout.setSpacing(12)

        self._exercise_title = QLabel("Select an exercise")
        self._exercise_title.setObjectName("fitnessDashExerciseTitle")
        self._exercise_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._exercise_title.setWordWrap(True)
        self._exercise_title.setStyleSheet("color: #111827;")
        _apply_pixel_font(self._exercise_title, pixel_size=24, weight=QFont.Weight.ExtraBold)

        self._value_spin = QSpinBox()
        self._value_spin.setObjectName("fitnessDashValueSpin")
        self._value_spin.setRange(0, _VALUE_MAXIMUM)
        self._value_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self._value_spin.setMinimumSize(280, 88)
        self._value_spin.setStyleSheet(_VALUE_STYLE)
        _apply_pixel_font(self._value_spin, pixel_size=48, weight=QFont.Weight.ExtraBold)
        self._value_spin.lineEdit().returnPressed.connect(self.add_requested.emit)

        self._unit_label = QLabel("")
        self._unit_label.setObjectName("fitnessDashUnitLabel")
        self._unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._unit_label.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(self._unit_label, pixel_size=16)
        self._unit_label.hide()

        self._type_combo = QComboBox()
        self._type_combo.setObjectName("fitnessDashTypeCombo")
        self._type_combo.setMinimumWidth(280)
        self._type_combo.setStyleSheet(_TYPE_STYLE)
        _apply_pixel_font(self._type_combo, pixel_size=16)
        self._type_combo.hide()

        add_button = QPushButton("➕ Add")  # noqa: RUF001
        add_button.setObjectName("fitnessDashAddButton")
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setMinimumSize(280, 64)
        add_button.setStyleSheet(_ADD_BUTTON_STYLE)
        _apply_pixel_font(add_button, pixel_size=20, weight=QFont.Weight.Bold)
        add_button.clicked.connect(self.add_requested.emit)

        self._sets_value = QLabel("0")
        self._sets_value.setObjectName("fitnessDashSetsValue")
        self._sets_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sets_value.setStyleSheet("color: #111827;")
        _apply_pixel_font(self._sets_value, pixel_size=64, weight=QFont.Weight.ExtraBold)

        sets_hint = QLabel("sets today")
        sets_hint.setObjectName("fitnessDashSetsHint")
        sets_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sets_hint.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(sets_hint, pixel_size=20, weight=QFont.Weight.DemiBold)

        center_layout.addStretch(1)
        center_layout.addWidget(self._exercise_title)
        center_layout.addWidget(self._value_spin, 0, Qt.AlignmentFlag.AlignHCenter)
        center_layout.addWidget(self._unit_label)
        center_layout.addWidget(self._type_combo, 0, Qt.AlignmentFlag.AlignHCenter)
        center_layout.addWidget(add_button, 0, Qt.AlignmentFlag.AlignHCenter)
        center_layout.addStretch(1)
        center_layout.addWidget(self._sets_value)
        center_layout.addWidget(sets_hint)

        row.addWidget(self._list, 2)
        row.addWidget(center, 3)
        outer.addWidget(pane)

    def _on_exercise_index_changed(self, current: QModelIndex, _previous: QModelIndex | None = None) -> None:
        name = ""
        if current.isValid():
            value = current.data(Qt.ItemDataRole.UserRole)
            name = str(value) if value else ""
        self._exercise_title.setText(name or "Select an exercise")
        self.exercise_changed.emit(name)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("FitnessDashboardWidget { background: #FFFFFF; }")
        self._model = QStandardItemModel(self)
        self._build_ui()
```

</details>

### ⚙️ Method `focus_value`

```python
def focus_value(self) -> None
```

Move keyboard focus to the value field and select its text.

<details>
<summary>Code:</summary>

```python
def focus_value(self) -> None:
        self._value_spin.setFocus()
        self._value_spin.selectAll()
```

</details>

### ⚙️ Method `selected_exercise`

```python
def selected_exercise(self) -> str
```

Return the selected exercise name, or an empty string.

<details>
<summary>Code:</summary>

```python
def selected_exercise(self) -> str:
        index = self._list.currentIndex()
        if not index.isValid():
            return ""
        name = index.data(Qt.ItemDataRole.UserRole)
        return str(name) if name else ""
```

</details>

### ⚙️ Method `selected_type`

```python
def selected_type(self) -> str
```

Return the selected exercise type, or an empty string.

<details>
<summary>Code:</summary>

```python
def selected_type(self) -> str:
        return self._type_combo.currentText().strip()
```

</details>

### ⚙️ Method `set_exercises`

```python
def set_exercises(self, items: list[FitnessDashboardExercise], *, selected: str | None = None) -> None
```

Replace the exercise list and optionally restore a selection.

Args:

- `items` (`list[FitnessDashboardExercise]`): Exercises to show.
- `selected` (`str | None`): Exercise name to keep selected.

<details>
<summary>Code:</summary>

```python
def set_exercises(
        self,
        items: list[FitnessDashboardExercise],
        *,
        selected: str | None = None,
    ) -> None:
        previous = selected if selected is not None else self.selected_exercise()
        self._list.blockSignals(True)  # noqa: FBT003
        self._model.clear()
        selected_row = 0
        for row, item in enumerate(items):
            letter = item.name[:1] if item.name else ""
            icon = make_circular_icon(item.icon, _DASHBOARD_ICON_SIZE, letter=letter)
            row_item = QStandardItem(item.name)
            row_item.setIcon(icon)
            row_item.setEditable(False)
            row_item.setData(item.name, Qt.ItemDataRole.UserRole)
            if item.name_local.strip():
                row_item.setData(item.name_local.strip(), NAME_LOCAL_ROLE)
            row_item.setSizeHint(QSize(0, _DASHBOARD_ICON_SIZE + 16))
            self._model.appendRow(row_item)
            if previous and item.name == previous:
                selected_row = row
        if self._model.rowCount() > 0:
            self._list.setCurrentIndex(self._model.index(selected_row, 0))
        self._list.blockSignals(False)  # noqa: FBT003
        self._on_exercise_index_changed(self._list.currentIndex())
```

</details>

### ⚙️ Method `set_today_sets`

```python
def set_today_sets(self, count: int) -> None
```

Update the large sets figure shown under the add controls.

Args:

- `count` (`int`): Number of process records logged today.

<details>
<summary>Code:</summary>

```python
def set_today_sets(self, count: int) -> None:
        self._sets_value.setText(format_today_sets(count))
```

</details>

### ⚙️ Method `set_types`

```python
def set_types(self, types: list[str], *, selected: str = '') -> None
```

Fill the type combo and show it only when types exist.

Args:

- `types` (`list[str]`): Type names for the selected exercise.
- `selected` (`str`): Type to preselect when present.

<details>
<summary>Code:</summary>

```python
def set_types(self, types: list[str], *, selected: str = "") -> None:
        self._type_combo.blockSignals(True)  # noqa: FBT003
        self._type_combo.clear()
        self._type_combo.addItem("")
        self._type_combo.addItems(types)
        if selected:
            index = self._type_combo.findText(selected)
            if index >= 0:
                self._type_combo.setCurrentIndex(index)
        self._type_combo.blockSignals(False)  # noqa: FBT003
        self._type_combo.setVisible(bool(types))
```

</details>

### ⚙️ Method `set_unit`

```python
def set_unit(self, unit: str) -> None
```

Show the unit of the selected exercise under the value field.

Args:

- `unit` (`str`): Unit of measurement, or empty when nothing is selected.

<details>
<summary>Code:</summary>

```python
def set_unit(self, unit: str) -> None:
        text = unit.strip()
        self._unit_label.setText(text)
        self._unit_label.setVisible(bool(text))
```

</details>

### ⚙️ Method `set_value`

```python
def set_value(self, value: int) -> None
```

Set the numeric value used for the next set.

Args:

- `value` (`int`): Count, weight, or other exercise quantity.

<details>
<summary>Code:</summary>

```python
def set_value(self, value: int) -> None:
        self._value_spin.setValue(max(0, min(value, _VALUE_MAXIMUM)))
```

</details>

### ⚙️ Method `value`

```python
def value(self) -> int
```

Return the numeric value entered for the next set.

<details>
<summary>Code:</summary>

```python
def value(self) -> int:
        return int(self._value_spin.value())
```

</details>

## 🔧 Function `format_today_sets`

```python
def format_today_sets(count: int) -> str
```

Format today's set count for the large dashboard number.

Args:

- `count` (`int`): Number of process records logged today.

Returns:

- `str`: Compact integer text without a unit suffix.

<details>
<summary>Code:</summary>

```python
def format_today_sets(count: int) -> str:
    return str(max(0, int(count)))
```

</details>

## 🔧 Function `make_circular_icon`

```python
def make_circular_icon(source: QIcon | QPixmap | None, size: int, *, letter: str = '') -> QIcon
```

Clip `source` to a circle, or draw a letter placeholder when missing.

Args:

- `source` (`QIcon | QPixmap | None`): Square exercise image, if any.
- `size` (`int`): Output width and height in pixels.
- `letter` (`str`): Fallback initial drawn on a gray circle.

Returns:

- `QIcon`: Circular icon suitable for a list decoration.

<details>
<summary>Code:</summary>

```python
def make_circular_icon(source: QIcon | QPixmap | None, size: int, *, letter: str = "") -> QIcon:
    size = max(size, 16)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    source_pixmap = _source_pixmap(source, size)
    if source_pixmap is not None:
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        scaled = source_pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x_offset = (size - scaled.width()) // 2
        y_offset = (size - scaled.height()) // 2
        painter.drawPixmap(x_offset, y_offset, scaled)
        painter.end()
        return QIcon(pixmap)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#E5E7EB"))
    painter.drawEllipse(0, 0, size, size)
    initial = letter.strip()[:1].upper()
    if initial:
        painter.setPen(QColor("#6B7280"))
        font = painter.font()
        font.setPixelSize(max(size // 2, 12))
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), int(Qt.AlignmentFlag.AlignCenter), initial)
    painter.end()
    return QIcon(pixmap)
```

</details>
