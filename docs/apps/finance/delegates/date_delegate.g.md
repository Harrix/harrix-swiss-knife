---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `date_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DateDelegate`](#%EF%B8%8F-class-datedelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)

</details>

## 🏛️ Class `DateDelegate`

```python
class DateDelegate(QStyledItemDelegate)
```

Delegate for date column in transactions table.

<details>
<summary>Code:</summary>

```python
class DateDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize DateDelegate.

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
        """Create a date editor for the date column.

        Args:

        - `parent` (`QWidget`): Parent widget.
        - `_option` (`QStyleOptionViewItem`): Style option.
        - `_index` (`QModelIndex | QPersistentModelIndex`): Model index.

        Returns:

        - `QWidget`: The created date editor.

        """
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDate(QDate.currentDate())
        editor.setDisplayFormat("yyyy-MM-dd")

        # Set white background for the editor
        editor.setStyleSheet("QDateEdit { background-color: white; }")

        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        date_edit = cast("QDateEdit", editor)
        current_value = index.data()
        if current_value:
            try:
                # Parse date string to date object
                date_obj = date_class.fromisoformat(str(current_value))
                date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except (ValueError, TypeError):
                date_edit.setDate(QDate.currentDate())

    def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        date_edit = cast("QDateEdit", editor)
        selected_date: QDate = date_edit.date()
        date_string: str = selected_date.toString("yyyy-MM-dd")
        model.setData(index, date_string, Qt.ItemDataRole.DisplayRole)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize DateDelegate.

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

Create a date editor for the date column.

Args:

- `parent` (`QWidget`): Parent widget.
- `_option` (`QStyleOptionViewItem`): Style option.
- `_index` (`QModelIndex | QPersistentModelIndex`): Model index.

Returns:

- `QWidget`: The created date editor.

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDate(QDate.currentDate())
        editor.setDisplayFormat("yyyy-MM-dd")

        # Set white background for the editor
        editor.setStyleSheet("QDateEdit { background-color: white; }")

        return editor
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
        date_edit = cast("QDateEdit", editor)
        current_value = index.data()
        if current_value:
            try:
                # Parse date string to date object
                date_obj = date_class.fromisoformat(str(current_value))
                date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except (ValueError, TypeError):
                date_edit.setDate(QDate.currentDate())
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
        date_edit = cast("QDateEdit", editor)
        selected_date: QDate = date_edit.date()
        date_string: str = selected_date.toString("yyyy-MM-dd")
        model.setData(index, date_string, Qt.ItemDataRole.DisplayRole)
```

</details>
