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

    def createEditor(self, parent: QObject, _option, _index: QModelIndex) -> QDateEdit:  # noqa: N802, ANN001
        """Create a date editor for the date column.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `_option`: Style option.
        - `_index` (`QModelIndex`): Model index.

        Returns:

        - `QDateEdit`: The created date editor.

        """
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDate(QDate.currentDate())
        editor.setDisplayFormat("yyyy-MM-dd")

        # Set white background for the editor
        editor.setStyleSheet("QDateEdit { background-color: white; }")

        return editor

    def setEditorData(self, editor: QDateEdit, index: QModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QDateEdit`): The editor widget.
        - `index` (`QModelIndex`): Model index.

        """
        current_value = index.data()
        if current_value:
            try:
                # Make the pendulum.DateTime object timezone-aware (UTC) to avoid naive datetime
                date_obj = pendulum.parse(str(current_value), strict=False).date()
                editor.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except (ValueError, TypeError):
                editor.setDate(QDate.currentDate())

    def setModelData(self, editor: QDateEdit, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QDateEdit`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex`): Model index.

        """
        selected_date: QDate = editor.date()
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
def createEditor(self, parent: QObject, _option, _index: QModelIndex) -> QDateEdit
```

Create a date editor for the date column.

Args:

- `parent` (`QObject`): Parent widget.
- `_option`: Style option.
- `_index` (`QModelIndex`): Model index.

Returns:

- `QDateEdit`: The created date editor.

<details>
<summary>Code:</summary>

```python
def createEditor(self, parent: QObject, _option, _index: QModelIndex) -> QDateEdit:  # noqa: N802, ANN001
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
def setEditorData(self, editor: QDateEdit, index: QModelIndex) -> None
```

Set the current value in the editor.

Args:

- `editor` (`QDateEdit`): The editor widget.
- `index` (`QModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QDateEdit, index: QModelIndex) -> None:  # noqa: N802
        current_value = index.data()
        if current_value:
            try:
                # Make the pendulum.DateTime object timezone-aware (UTC) to avoid naive datetime
                date_obj = pendulum.parse(str(current_value), strict=False).date()
                editor.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except (ValueError, TypeError):
                editor.setDate(QDate.currentDate())
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QDateEdit, model: QAbstractItemModel, index: QModelIndex) -> None
```

Set the data from the editor back to the model.

Args:

- `editor` (`QDateEdit`): The editor widget.
- `model` (`QAbstractItemModel`): The data model.
- `index` (`QModelIndex`): Model index.

<details>
<summary>Code:</summary>

```python
def setModelData(self, editor: QDateEdit, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        selected_date: QDate = editor.date()
        date_string: str = selected_date.toString("yyyy-MM-dd")
        model.setData(index, date_string, Qt.ItemDataRole.DisplayRole)
```

</details>
