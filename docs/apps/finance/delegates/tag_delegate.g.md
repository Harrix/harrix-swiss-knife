---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tag_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TagDelegate`](#%EF%B8%8F-class-tagdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)

</details>

## 🏛️ Class `TagDelegate`

```python
class TagDelegate(QStyledItemDelegate)
```

Delegate for tag column in transactions table.

<details>
<summary>Code:</summary>

```python
class TagDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject | None = None, tags: list[str] | None = None) -> None:
        """Initialize the tag delegate."""
        super().__init__(parent)
        self.tags = tags or []

    def createEditor(self, parent: QObject, _: QStyleOptionViewItem, _index: QModelIndex) -> QComboBox:  # noqa: N802
        """Create a combo box editor for the tag column.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `_` (`QStyleOptionViewItem`): Style option (unused).
        - `_index` (`QModelIndex`): Model index (unused).

        Returns:

        - `QComboBox`: The created combo box editor.

        """
        combo: QComboBox = QComboBox(cast("QWidget", parent))
        combo.setEditable(True)

        # Set white background for the editor
        combo.setStyleSheet("QComboBox { background-color: white; }")

        # Add tags to combo box
        for tag in self.tags:
            combo.addItem(tag)

        return combo

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QComboBox`): The editor widget.
        - `index` (`QModelIndex`): Model index.

        """
        current_value = index.data()
        if current_value:
            # Find the exact value in the combo box
            index_in_combo: int = editor.findText(current_value)
            if index_in_combo >= 0:
                editor.setCurrentIndex(index_in_combo)
            else:
                # If not found, set as current text
                editor.setCurrentText(current_value)

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QComboBox`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex`): Model index.

        """
        selected_text: str = editor.currentText()
        if selected_text:
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, tags: list[str] | None = None) -> None
```

Initialize the tag delegate.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None, tags: list[str] | None = None) -> None:
        super().__init__(parent)
        self.tags = tags or []
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QObject, _: QStyleOptionViewItem, _index: QModelIndex) -> QComboBox
```

Create a combo box editor for the tag column.

Args:

- `parent` (`QObject`): Parent widget.
- `_` (`QStyleOptionViewItem`): Style option (unused).
- `_index` (`QModelIndex`): Model index (unused).

Returns:

- `QComboBox`: The created combo box editor.

<details>
<summary>Code:</summary>

```python
def createEditor(self, parent: QObject, _: QStyleOptionViewItem, _index: QModelIndex) -> QComboBox:  # noqa: N802
        combo: QComboBox = QComboBox(cast("QWidget", parent))
        combo.setEditable(True)

        # Set white background for the editor
        combo.setStyleSheet("QComboBox { background-color: white; }")

        # Add tags to combo box
        for tag in self.tags:
            combo.addItem(tag)

        return combo
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None
```

Set the current value in the editor.

Args:

- `editor` (`QComboBox`): The editor widget.
- `index` (`QModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:  # noqa: N802
        current_value = index.data()
        if current_value:
            # Find the exact value in the combo box
            index_in_combo: int = editor.findText(current_value)
            if index_in_combo >= 0:
                editor.setCurrentIndex(index_in_combo)
            else:
                # If not found, set as current text
                editor.setCurrentText(current_value)
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None
```

Set the data from the editor back to the model.

Args:

- `editor` (`QComboBox`): The editor widget.
- `model` (`QAbstractItemModel`): The data model.
- `index` (`QModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        selected_text: str = editor.currentText()
        if selected_text:
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>
