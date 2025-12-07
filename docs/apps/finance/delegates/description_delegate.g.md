---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `description_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DescriptionDelegate`](#%EF%B8%8F-class-descriptiondelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)

</details>

## 🏛️ Class `DescriptionDelegate`

```python
class DescriptionDelegate(QStyledItemDelegate)
```

Delegate for description column in transactions table.

<details>
<summary>Code:</summary>

```python
class DescriptionDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize DescriptionDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.

        """
        super().__init__(parent)

    def createEditor(self, parent: QObject, _option: object, _index: QModelIndex) -> QLineEdit:  # noqa: N802
        """Create a line edit editor for the description column.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `_option` (`object`): Style option.
        - `_index` (`QModelIndex`): Model index.

        Returns:

        - `QLineEdit`: The created line edit editor.

        """
        editor = QLineEdit(cast("QWidget", parent))

        # Set white background for the editor
        editor.setStyleSheet("QLineEdit { background-color: white; }")

        return editor

    def setEditorData(self, editor: QLineEdit, index: QModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QLineEdit`): The editor widget.
        - `index` (`QModelIndex`): Model index.

        """
        current_value = index.data()
        if current_value:
            editor.setText(str(current_value))

    def setModelData(self, editor: QLineEdit, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QLineEdit`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex`): Model index.

        """
        text = editor.text()
        model.setData(index, text, Qt.ItemDataRole.DisplayRole)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize DescriptionDelegate.

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
def createEditor(self, parent: QObject, _option: object, _index: QModelIndex) -> QLineEdit
```

Create a line edit editor for the description column.

Args:

- `parent` (`QObject`): Parent widget.
- `_option` (`object`): Style option.
- `_index` (`QModelIndex`): Model index.

Returns:

- `QLineEdit`: The created line edit editor.

<details>
<summary>Code:</summary>

```python
def createEditor(self, parent: QObject, _option: object, _index: QModelIndex) -> QLineEdit:  # noqa: N802
        editor = QLineEdit(cast("QWidget", parent))

        # Set white background for the editor
        editor.setStyleSheet("QLineEdit { background-color: white; }")

        return editor
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QLineEdit, index: QModelIndex) -> None
```

Set the current value in the editor.

Args:

- `editor` (`QLineEdit`): The editor widget.
- `index` (`QModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QLineEdit, index: QModelIndex) -> None:  # noqa: N802
        current_value = index.data()
        if current_value:
            editor.setText(str(current_value))
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QLineEdit, model: QAbstractItemModel, index: QModelIndex) -> None
```

Set the data from the editor back to the model.

Args:

- `editor` (`QLineEdit`): The editor widget.
- `model` (`QAbstractItemModel`): The data model.
- `index` (`QModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setModelData(self, editor: QLineEdit, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        text = editor.text()
        model.setData(index, text, Qt.ItemDataRole.DisplayRole)
```

</details>
