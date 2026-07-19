---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `is_drink_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IsDrinkDelegate`](#️-class-isdrinkdelegate)
  - [⚙️ Method `createEditor`](#️-method-createeditor)
  - [⚙️ Method `displayText`](#️-method-displaytext)
  - [⚙️ Method `setEditorData`](#️-method-seteditordata)
  - [⚙️ Method `setModelData`](#️-method-setmodeldata)
  - [⚙️ Method `updateEditorGeometry`](#️-method-updateeditorgeometry)
- [🔧 Function `is_drink_to_model`](#-function-is_drink_to_model)
- [🔧 Function `parse_is_drink_cell`](#-function-parse_is_drink_cell)

</details>

## 🏛️ Class `IsDrinkDelegate`

```python
class IsDrinkDelegate(QStyledItemDelegate)
```

Show drink emoji in view mode; edit with a checkbox storing 1/empty.

<details>
<summary>Code:</summary>

```python
class IsDrinkDelegate(QStyledItemDelegate):

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a full-cell editor with a centered native checkbox."""
        container = QWidget(parent)
        self._apply_editor_row_background(container, option)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        checkbox = QCheckBox(container)
        checkbox.setText("")
        checkbox.stateChanged.connect(lambda _state, editor=container: self._commit_checkbox_editor(editor))
        layout.addWidget(checkbox)

        container.setProperty("_is_drink_checkbox", checkbox)
        return container

    def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Map stored model value to emoji display text.

        Args:

        - `value` (`object`): Raw model value.
        - `_locale` (`QLocale | QLocale.Language`): Locale (unused).

        Returns:

        - `str`: Drink emoji or empty string.

        """
        return DRINK_EMOJI if parse_is_drink_cell(value) else ""

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Load model value into the checkbox editor."""
        checkbox = _checkbox_from_editor(editor)
        if checkbox is None:
            return
        checkbox.blockSignals(True)  # noqa: FBT003
        try:
            checkbox.setChecked(parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)))
        finally:
            checkbox.blockSignals(False)  # noqa: FBT003

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write checkbox state back to the model as 1 or empty."""
        checkbox = _checkbox_from_editor(editor)
        if checkbox is None:
            return
        model.setData(index, is_drink_to_model(checked=checkbox.isChecked()), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Resize the editor to cover the entire table cell."""
        editor.setGeometry(option.rect)

    @staticmethod
    def _apply_editor_row_background(editor: QWidget, option: QStyleOptionViewItem) -> None:
        """Match the editor background to the table row without overriding native checkbox style."""
        brush = option.backgroundBrush
        if brush.style() != Qt.BrushStyle.NoBrush and brush.color().isValid():
            bg = brush.color()
        else:
            bg = QColor(255, 255, 255)
        palette = editor.palette()
        palette.setColor(QPalette.ColorRole.Window, bg)
        palette.setColor(QPalette.ColorRole.Base, bg)
        editor.setPalette(palette)
        editor.setAutoFillBackground(True)

    def _commit_checkbox_editor(self, editor: QWidget) -> None:
        """Commit editor data when the user toggles the checkbox."""
        self.commitData.emit(editor)
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Create a full-cell editor with a centered native checkbox.

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        container = QWidget(parent)
        self._apply_editor_row_background(container, option)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        checkbox = QCheckBox(container)
        checkbox.setText("")
        checkbox.stateChanged.connect(lambda _state, editor=container: self._commit_checkbox_editor(editor))
        layout.addWidget(checkbox)

        container.setProperty("_is_drink_checkbox", checkbox)
        return container
```

</details>

### ⚙️ Method `displayText`

```python
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str
```

Map stored model value to emoji display text.

Args:

- `value` (`object`): Raw model value.
- `_locale` (`QLocale | QLocale.Language`): Locale (unused).

Returns:

- `str`: Drink emoji or empty string.

<details>
<summary>Code:</summary>

```python
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        return DRINK_EMOJI if parse_is_drink_cell(value) else ""
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None
```

Load model value into the checkbox editor.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        checkbox = _checkbox_from_editor(editor)
        if checkbox is None:
            return
        checkbox.blockSignals(True)  # noqa: FBT003
        try:
            checkbox.setChecked(parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)))
        finally:
            checkbox.blockSignals(False)  # noqa: FBT003
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None
```

Write checkbox state back to the model as 1 or empty.

<details>
<summary>Code:</summary>

```python
def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        checkbox = _checkbox_from_editor(editor)
        if checkbox is None:
            return
        model.setData(index, is_drink_to_model(checked=checkbox.isChecked()), Qt.ItemDataRole.EditRole)
```

</details>

### ⚙️ Method `updateEditorGeometry`

```python
def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> None
```

Resize the editor to cover the entire table cell.

<details>
<summary>Code:</summary>

```python
def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        editor.setGeometry(option.rect)
```

</details>

## 🔧 Function `is_drink_to_model`

```python
def is_drink_to_model() -> str
```

Convert checkbox state to food log model storage.

Args:

- `checked` (`bool`): Whether the drink checkbox is checked.

Returns:

- `str`: `1` when checked, empty string otherwise.

<details>
<summary>Code:</summary>

```python
def is_drink_to_model(*, checked: bool) -> str:
    return "1" if checked else ""
```

</details>

## 🔧 Function `parse_is_drink_cell`

```python
def parse_is_drink_cell(value: object) -> bool
```

Return whether a model cell value represents a drink.

Args:

- `value` (`object`): Raw cell value from the model.

Returns:

- `bool`: `True` if the value indicates a drink.

<details>
<summary>Code:</summary>

```python
def parse_is_drink_cell(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip().lower()
    if not text:
        return False
    return text in _TRUTHY_IS_DRINK or text == DRINK_EMOJI
```

</details>
