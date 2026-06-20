---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `combo_box_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ComboBoxDelegate`](#️-class-comboboxdelegate)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `createEditor`](#️-method-createeditor)
  - [⚙️ Method `setEditorData`](#️-method-seteditordata)
  - [⚙️ Method `setModelData`](#️-method-setmodeldata)

</details>

## 🏛️ Class `ComboBoxDelegate`

```python
class ComboBoxDelegate(QStyledItemDelegate)
```

Delegate that edits a cell with a QComboBox and optional empty leading item.

<details>
<summary>Code:</summary>

```python
class ComboBoxDelegate(QStyledItemDelegate):

    def __init__(
        self,
        parent: QObject | None = None,
        *,
        items: list[str] | None = None,
        editable: bool = False,
        leading_empty_item: bool = False,
        strip_values: bool = False,
        write_empty_value: bool = False,
    ) -> None:
        """Initialize ComboBoxDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.
        - `items` (`list[str] | None`): Combo box entries (after optional leading empty item).
        - `editable` (`bool`): Whether the combo allows custom text (tag column).
        - `leading_empty_item` (`bool`): Insert blank item at index 0 before `items`.
        - `strip_values` (`bool`): Strip whitespace in `setModelData` before writing.
        - `write_empty_value` (`bool`): Write model even when the value is empty after strip.

        """
        super().__init__(parent)
        self.items: list[str] = list(items or [])
        self.editable = editable
        self.leading_empty_item = leading_empty_item
        self.strip_values = strip_values
        self.write_empty_value = write_empty_value

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a combo box editor populated from `items`."""
        combo = QComboBox(parent)
        combo.setEditable(self.editable)

        apply_white_editor_background(combo, "QComboBox")

        if self.leading_empty_item:
            combo.insertItem(0, "")

        for item in self.items:
            text = str(item).strip() if item is not None else ""
            if self.leading_empty_item and not text:
                continue
            combo.addItem(item if item is not None else "")

        return combo

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current cell value in the combo box."""
        combo = cast("QComboBox", editor)
        raw = index.data()
        current_value = str(raw) if raw is not None else ""

        if self.leading_empty_item and not current_value.strip():
            combo.setCurrentIndex(0)
            return

        if current_value:
            index_in_combo = combo.findText(current_value)
            if index_in_combo >= 0:
                combo.setCurrentIndex(index_in_combo)
            elif self.editable:
                combo.setCurrentText(current_value)

    def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Write the selected combo value back to the model."""
        combo = cast("QComboBox", editor)
        selected_text = combo.currentText()
        if self.strip_values:
            selected_text = selected_text.strip()

        if selected_text or self.write_empty_value:
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize ComboBoxDelegate.

Args:

- `parent` (`QObject | None`): Parent object for the delegate.
- `items` (`list[str] | None`): Combo box entries (after optional leading empty item).
- `editable` (`bool`): Whether the combo allows custom text (tag column).
- `leading_empty_item` (`bool`): Insert blank item at index 0 before `items`.
- `strip_values` (`bool`): Strip whitespace in `setModelData` before writing.
- `write_empty_value` (`bool`): Write model even when the value is empty after strip.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QObject | None = None,
        *,
        items: list[str] | None = None,
        editable: bool = False,
        leading_empty_item: bool = False,
        strip_values: bool = False,
        write_empty_value: bool = False,
    ) -> None:
        super().__init__(parent)
        self.items: list[str] = list(items or [])
        self.editable = editable
        self.leading_empty_item = leading_empty_item
        self.strip_values = strip_values
        self.write_empty_value = write_empty_value
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Create a combo box editor populated from `items`.

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        combo = QComboBox(parent)
        combo.setEditable(self.editable)

        apply_white_editor_background(combo, "QComboBox")

        if self.leading_empty_item:
            combo.insertItem(0, "")

        for item in self.items:
            text = str(item).strip() if item is not None else ""
            if self.leading_empty_item and not text:
                continue
            combo.addItem(item if item is not None else "")

        return combo
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None
```

Set the current cell value in the combo box.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        combo = cast("QComboBox", editor)
        raw = index.data()
        current_value = str(raw) if raw is not None else ""

        if self.leading_empty_item and not current_value.strip():
            combo.setCurrentIndex(0)
            return

        if current_value:
            index_in_combo = combo.findText(current_value)
            if index_in_combo >= 0:
                combo.setCurrentIndex(index_in_combo)
            elif self.editable:
                combo.setCurrentText(current_value)
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None
```

Write the selected combo value back to the model.

<details>
<summary>Code:</summary>

```python
def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        combo = cast("QComboBox", editor)
        selected_text = combo.currentText()
        if self.strip_values:
            selected_text = selected_text.strip()

        if selected_text or self.write_empty_value:
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>
