---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `is_drink_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IsDrinkDelegate`](#%EF%B8%8F-class-isdrinkdelegate)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)
  - [⚙️ Method `updateEditorGeometry`](#%EF%B8%8F-method-updateeditorgeometry)
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
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a checkbox editor for the Is Drink column."""
        editor = QCheckBox(parent)
        editor.stateChanged.connect(lambda: self.commitData.emit(editor))
        apply_white_editor_background(editor, "QCheckBox")
        return editor

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
        checkbox = editor if isinstance(editor, QCheckBox) else None
        if checkbox is None:
            return
        checkbox.setChecked(parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)))

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write checkbox state back to the model as 1 or empty."""
        checkbox = editor if isinstance(editor, QCheckBox) else None
        if checkbox is None:
            return
        model.setData(index, is_drink_to_model(checked=checkbox.isChecked()), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Position the checkbox editor inside the cell."""
        editor.setGeometry(option.rect)
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Create a checkbox editor for the Is Drink column.

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        editor = QCheckBox(parent)
        editor.stateChanged.connect(lambda: self.commitData.emit(editor))
        apply_white_editor_background(editor, "QCheckBox")
        return editor
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
        checkbox = editor if isinstance(editor, QCheckBox) else None
        if checkbox is None:
            return
        checkbox.setChecked(parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)))
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
        checkbox = editor if isinstance(editor, QCheckBox) else None
        if checkbox is None:
            return
        model.setData(index, is_drink_to_model(checked=checkbox.isChecked()), Qt.ItemDataRole.EditRole)
```

</details>

### ⚙️ Method `updateEditorGeometry`

```python
def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> None
```

Position the checkbox editor inside the cell.

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

- `str`: `"1"` when checked, empty string otherwise.

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

- `bool`: True if the value indicates a drink.

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
