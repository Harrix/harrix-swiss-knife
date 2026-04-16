---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_combo_box_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CategoryComboBoxDelegate`](#%EF%B8%8F-class-categorycomboboxdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)

</details>

## 🏛️ Class `CategoryComboBoxDelegate`

```python
class CategoryComboBoxDelegate(QStyledItemDelegate)
```

Delegate for category column in transactions table with dropdown list.

<details>
<summary>Code:</summary>

```python
class CategoryComboBoxDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject | None = None, categories: list[str] | None = None) -> None:
        """Initialize CategoryComboBoxDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object.
        - `categories` (`list[str] | None`): List of category names for the combo box.

        """
        super().__init__(parent)
        self.categories = categories or []

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a combo box editor for the category column.

        Args:

        - `parent` (`QWidget`): Parent widget.
        - `_option` (`QStyleOptionViewItem`): Style option.
        - `_index` (`QModelIndex | QPersistentModelIndex`): Model index.

        Returns:

        - `QWidget`: The created combo box editor.

        """
        combo = QComboBox(parent)
        combo.setEditable(False)

        apply_white_editor_background(combo, "QComboBox")

        # Add categories to combo box
        for category in self.categories:
            combo.addItem(category)

        return combo

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        combo = cast("QComboBox", editor)
        current_value = index.data()
        if current_value:
            # Find the exact value in the combo box
            index_in_combo = combo.findText(current_value)
            if index_in_combo >= 0:
                combo.setCurrentIndex(index_in_combo)

    def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        combo = cast("QComboBox", editor)
        selected_text = combo.currentText()
        if selected_text:
            # Check if this is an income category and add suffix if needed
            # This logic should match the logic used in _save_transaction_data
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, categories: list[str] | None = None) -> None
```

Initialize CategoryComboBoxDelegate.

Args:

- `parent` (`QObject | None`): Parent object.
- `categories` (`list[str] | None`): List of category names for the combo box.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None, categories: list[str] | None = None) -> None:
        super().__init__(parent)
        self.categories = categories or []
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Create a combo box editor for the category column.

Args:

- `parent` (`QWidget`): Parent widget.
- `_option` (`QStyleOptionViewItem`): Style option.
- `_index` (`QModelIndex | QPersistentModelIndex`): Model index.

Returns:

- `QWidget`: The created combo box editor.

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
        combo.setEditable(False)

        apply_white_editor_background(combo, "QComboBox")

        # Add categories to combo box
        for category in self.categories:
            combo.addItem(category)

        return combo
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None
```

Set the current value in the editor.

Args:

- `editor` (`QWidget`): The editor widget.
- `index` (`QModelIndex | QPersistentModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        combo = cast("QComboBox", editor)
        current_value = index.data()
        if current_value:
            # Find the exact value in the combo box
            index_in_combo = combo.findText(current_value)
            if index_in_combo >= 0:
                combo.setCurrentIndex(index_in_combo)
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None
```

Set the data from the editor back to the model.

Args:

- `editor` (`QWidget`): The editor widget.
- `model` (`QAbstractItemModel`): The data model.
- `index` (`QModelIndex | QPersistentModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        combo = cast("QComboBox", editor)
        selected_text = combo.currentText()
        if selected_text:
            # Check if this is an income category and add suffix if needed
            # This logic should match the logic used in _save_transaction_data
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>
