---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `readonly_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ReadOnlyDelegate`](#%EF%B8%8F-class-readonlydelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)

</details>

## 🏛️ Class `ReadOnlyDelegate`

```python
class ReadOnlyDelegate(QStyledItemDelegate)
```

Delegate for read-only columns that display data but don't allow editing.

This delegate provides display formatting for read-only columns while
preventing any editing functionality.

<details>
<summary>Code:</summary>

```python
class ReadOnlyDelegate(QStyledItemDelegate):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the read-only delegate.

        Args:

        - `parent` (`QWidget | None`): The parent widget. Defaults to `None`.

        """
        super().__init__(parent)

    def createEditor(self, _parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex) -> None:  # noqa: N802
        """Prevent creation of any editor for read-only columns.

        Args:

        - `_parent` (`QWidget`): The parent widget for the editor.
        - `_option` (`QStyleOptionViewItem`): The style options for the item.
        - `_index` (`QModelIndex`): The model index of the item being edited.

        Returns:

        - `None`: Always returns None to prevent editing.

        """
        # Return None to prevent any editing
        return

    def editorEvent(  # noqa: N802
        self,
        _event: "QEvent",
        _model: "QAbstractItemModel",
        _option: QStyleOptionViewItem,
        _index: QModelIndex,
    ) -> bool:
        """Prevent editor events for read-only columns.

        Args:

        - `_event` (`QEvent`): The event being processed.
        - `_model` (`QAbstractItemModel`): The model containing the data.
        - `_option` (`QStyleOptionViewItem`): The style options for the item.
        - `_index` (`QModelIndex`): The model index of the item.

        Returns:

        - `bool`: Always returns False to prevent editing.

        """
        # Return False to prevent any editor events
        return False
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the read-only delegate.

Args:

- `parent` (`QWidget | None`): The parent widget. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, _parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex) -> None
```

Prevent creation of any editor for read-only columns.

Args:

- `_parent` (`QWidget`): The parent widget for the editor.
- `_option` (`QStyleOptionViewItem`): The style options for the item.
- `_index` (`QModelIndex`): The model index of the item being edited.

Returns:

- `None`: Always returns None to prevent editing.

<details>
<summary>Code:</summary>

```python
def createEditor(self, _parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex) -> None:  # noqa: N802
        # Return None to prevent any editing
        return
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, _event: "QEvent", _model: "QAbstractItemModel", _option: QStyleOptionViewItem, _index: QModelIndex) -> bool
```

Prevent editor events for read-only columns.

Args:

- `_event` (`QEvent`): The event being processed.
- `_model` (`QAbstractItemModel`): The model containing the data.
- `_option` (`QStyleOptionViewItem`): The style options for the item.
- `_index` (`QModelIndex`): The model index of the item.

Returns:

- `bool`: Always returns False to prevent editing.

<details>
<summary>Code:</summary>

```python
def editorEvent(  # noqa: N802
        self,
        _event: "QEvent",
        _model: "QAbstractItemModel",
        _option: QStyleOptionViewItem,
        _index: QModelIndex,
    ) -> bool:
        # Return False to prevent any editor events
        return False
```

</details>
