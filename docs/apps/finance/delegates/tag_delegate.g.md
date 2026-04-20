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

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a combo box editor for the tag column.

        Args:

        - `parent` (`QWidget`): Parent widget.
        - `_` (`QStyleOptionViewItem`): Style option (unused).
        - `_index` (`QModelIndex | QPersistentModelIndex`): Model index (unused).

        Returns:

        - `QWidget`: The created combo box editor.

        """
        combo: QComboBox = QComboBox(parent)
        combo.setEditable(True)

        apply_white_editor_background(combo, "QComboBox")

        # Empty option first so the tag can be cleared from the dropdown
        combo.insertItem(0, "")
        for tag in self.tags:
            if tag and str(tag).strip():
                combo.addItem(tag)

        return combo

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        combo = cast("QComboBox", editor)
        raw = index.data()
        current_value = str(raw) if raw is not None else ""
        if not current_value.strip():
            combo.setCurrentIndex(0)
            return
        index_in_combo: int = combo.findText(current_value)
        if index_in_combo >= 0:
            combo.setCurrentIndex(index_in_combo)
        else:
            combo.setCurrentText(current_value)

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
        selected_text: str = combo.currentText().strip()
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
def createEditor(self, parent: QWidget, _: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Create a combo box editor for the tag column.

Args:

- `parent` (`QWidget`): Parent widget.
- `_` (`QStyleOptionViewItem`): Style option (unused).
- `_index` (`QModelIndex | QPersistentModelIndex`): Model index (unused).

Returns:

- `QWidget`: The created combo box editor.

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        combo: QComboBox = QComboBox(parent)
        combo.setEditable(True)

        apply_white_editor_background(combo, "QComboBox")

        # Empty option first so the tag can be cleared from the dropdown
        combo.insertItem(0, "")
        for tag in self.tags:
            if tag and str(tag).strip():
                combo.addItem(tag)

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
        raw = index.data()
        current_value = str(raw) if raw is not None else ""
        if not current_value.strip():
            combo.setCurrentIndex(0)
            return
        index_in_combo: int = combo.findText(current_value)
        if index_in_combo >= 0:
            combo.setCurrentIndex(index_in_combo)
        else:
            combo.setCurrentText(current_value)
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
        selected_text: str = combo.currentText().strip()
        model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
```

</details>
