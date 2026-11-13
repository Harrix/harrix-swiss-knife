---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `yes_no_combo_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `YesNoComboDelegate`](#%EF%B8%8F-class-yesnocombodelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)
  - [⚙️ Method `updateEditorGeometry`](#%EF%B8%8F-method-updateeditorgeometry)

</details>

## 🏛️ Class `YesNoComboDelegate`

```python
class YesNoComboDelegate(QStyledItemDelegate)
```

Delegate that edits values using a non-editable Yes/No combo box.

<details>
<summary>Code:</summary>

```python
class YesNoComboDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize YesNoComboDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.

        """
        super().__init__(parent)

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a Yes/No combo box editor."""
        combo = QComboBox(parent)
        combo.addItems(list(_YES_NO_ITEMS))
        combo.setEditable(False)

        apply_white_editor_background(combo, "QComboBox")
        return combo

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current Yes/No value in the editor."""
        combo = cast("QComboBox", editor)
        value = index.data()
        text = str(value) if value is not None else ""
        if text not in _YES_NO_ITEMS:
            text = "No"
        combo.setCurrentText(text)

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write Yes/No selection back to the model."""
        combo = cast("QComboBox", editor)
        model.setData(index, combo.currentText(), Qt.ItemDataRole.DisplayRole)

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Size the editor to the cell rectangle."""
        editor.setGeometry(option.rect)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize YesNoComboDelegate.

Args:

- `parent` (`QObject | None`): Parent object for the delegate.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Create a Yes/No combo box editor.

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
        combo.addItems(list(_YES_NO_ITEMS))
        combo.setEditable(False)

        apply_white_editor_background(combo, "QComboBox")
        return combo
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None
```

Set the current Yes/No value in the editor.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        combo = cast("QComboBox", editor)
        value = index.data()
        text = str(value) if value is not None else ""
        if text not in _YES_NO_ITEMS:
            text = "No"
        combo.setCurrentText(text)
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None
```

Write Yes/No selection back to the model.

<details>
<summary>Code:</summary>

```python
def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        combo = cast("QComboBox", editor)
        model.setData(index, combo.currentText(), Qt.ItemDataRole.DisplayRole)
```

</details>

### ⚙️ Method `updateEditorGeometry`

```python
def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> None
```

Size the editor to the cell rectangle.

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
