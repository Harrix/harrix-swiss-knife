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
  - [⚙️ Method `helpEvent`](#%EF%B8%8F-method-helpevent)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
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

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a line edit editor for the description column.

        Args:

        - `parent` (`QWidget`): Parent widget.
        - `_option` (`QStyleOptionViewItem`): Style option.
        - `_index` (`QModelIndex | QPersistentModelIndex`): Model index.

        Returns:

        - `QWidget`: The created line edit editor.

        """
        editor = QLineEdit(parent)

        apply_white_editor_background(editor, "QLineEdit")

        return editor

    def helpEvent(  # noqa: N802
        self,
        event: QHelpEvent,
        view: QWidget | None,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Show the full description when the cell text is elided."""
        del option
        if view is None:
            return False
        text = index.data(Qt.ItemDataRole.DisplayRole)
        tip = "" if text is None else str(text).strip()
        if not tip:
            return False
        QToolTip.showText(event.globalPos(), tip, view)
        return True

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint description text with Fluent ink when the model fg is stuck dark."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        host = opt.widget if isinstance(opt.widget, QWidget) else None
        fluent = palette_for(host)
        # Soft-blue selection keeps dark HighlightedText; only fix unselected rows.
        if fluent.dark and not selected and _foreground_too_dark(index, opt):
            ink = mix(fluent.window_bg, fluent.text_primary)
            opt.palette.setColor(QPalette.ColorRole.Text, ink)
            opt.palette.setColor(QPalette.ColorRole.WindowText, ink)
        super().paint(painter, opt, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        line_edit = cast("QLineEdit", editor)
        current_value = index.data()
        if current_value:
            line_edit.setText(str(current_value))

    def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        line_edit = cast("QLineEdit", editor)
        text = line_edit.text()
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
def createEditor(self, parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Create a line edit editor for the description column.

Args:

- `parent` (`QWidget`): Parent widget.
- `_option` (`QStyleOptionViewItem`): Style option.
- `_index` (`QModelIndex | QPersistentModelIndex`): Model index.

Returns:

- `QWidget`: The created line edit editor.

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        editor = QLineEdit(parent)

        apply_white_editor_background(editor, "QLineEdit")

        return editor
```

</details>

### ⚙️ Method `helpEvent`

```python
def helpEvent(self, event: QHelpEvent, view: QWidget | None, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Show the full description when the cell text is elided.

<details>
<summary>Code:</summary>

```python
def helpEvent(  # noqa: N802
        self,
        event: QHelpEvent,
        view: QWidget | None,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        del option
        if view is None:
            return False
        text = index.data(Qt.ItemDataRole.DisplayRole)
        tip = "" if text is None else str(text).strip()
        if not tip:
            return False
        QToolTip.showText(event.globalPos(), tip, view)
        return True
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint description text with Fluent ink when the model fg is stuck dark.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        host = opt.widget if isinstance(opt.widget, QWidget) else None
        fluent = palette_for(host)
        # Soft-blue selection keeps dark HighlightedText; only fix unselected rows.
        if fluent.dark and not selected and _foreground_too_dark(index, opt):
            ink = mix(fluent.window_bg, fluent.text_primary)
            opt.palette.setColor(QPalette.ColorRole.Text, ink)
            opt.palette.setColor(QPalette.ColorRole.WindowText, ink)
        super().paint(painter, opt, index)
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
        line_edit = cast("QLineEdit", editor)
        current_value = index.data()
        if current_value:
            line_edit.setText(str(current_value))
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
        line_edit = cast("QLineEdit", editor)
        text = line_edit.text()
        model.setData(index, text, Qt.ItemDataRole.DisplayRole)
```

</details>
