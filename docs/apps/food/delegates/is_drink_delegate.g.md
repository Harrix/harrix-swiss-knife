---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `is_drink_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IsDrinkDelegate`](#%EF%B8%8F-class-isdrinkdelegate)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
  - [⚙️ Method `updateEditorGeometry`](#%EF%B8%8F-method-updateeditorgeometry)
- [🔧 Function `is_drink_to_model`](#-function-is_drink_to_model)
- [🔧 Function `parse_is_drink_cell`](#-function-parse_is_drink_cell)

</details>

## 🏛️ Class `IsDrinkDelegate`

```python
class IsDrinkDelegate(QStyledItemDelegate)
```

Show Lucide coffee in view mode; edit with a checkbox storing 1/empty.

<details>
<summary>Code:</summary>

```python
class IsDrinkDelegate(QStyledItemDelegate):

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a full-cell editor with a centered native checkbox and drink icon."""
        container = QWidget(parent)
        self._apply_editor_row_background(container, option)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        checkbox = QCheckBox(container)
        checkbox.setText("")
        install_drink_checkbox_icon(checkbox, size=DRINK_ICON_SIZE)
        checkbox.stateChanged.connect(lambda _state, editor=container: self._commit_checkbox_editor(editor))
        layout.addWidget(checkbox)

        container.setProperty("_is_drink_checkbox", checkbox)
        return container

    def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide text; the drink marker is painted as a Lucide icon."""
        return ""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the colored coffee icon when the row is a drink."""
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else None
        if style is not None:
            style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)
        if not parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)):
            return
        icon = create_drink_icon(DRINK_ICON_SIZE)
        side = min(option.rect.width(), option.rect.height(), DRINK_ICON_SIZE + 4)
        icon.paint(
            painter,
            option.rect.x() + (option.rect.width() - side) // 2,
            option.rect.y() + (option.rect.height() - side) // 2,
            side,
            side,
        )

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Load model value into the checkbox editor."""
        checkbox = _checkbox_from_editor(editor)
        if checkbox is None:
            return
        checkbox.blockSignals(True)  # noqa: FBT003
        try:
            checkbox.setChecked(parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)))
        finally:
            checkbox.blockSignals(False)  # noqa: FBT003

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write checkbox state back to the model as 1 or empty."""
        checkbox = _checkbox_from_editor(editor)
        if checkbox is None:
            return
        model.setData(index, is_drink_to_model(checked=checkbox.isChecked()), Qt.ItemDataRole.EditRole)

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Keep the drink column wide enough for the coffee icon."""
        hint = super().sizeHint(option, index)
        return QSize(max(hint.width(), DRINK_ICON_SIZE + 12), max(hint.height(), DRINK_ICON_SIZE + 8))

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Resize the editor to cover the entire table cell."""
        editor.setGeometry(option.rect)

    @staticmethod
    def _apply_editor_row_background(editor: QWidget, option: QStyleOptionViewItem) -> None:
        """Match the editor background to the table row without overriding native checkbox style."""
        brush = option.backgroundBrush
        if brush.style() != Qt.BrushStyle.NoBrush and brush.color().isValid():
            bg = brush.color()
        else:
            bg = QColor(255, 255, 255)
        palette = editor.palette()
        palette.setColor(QPalette.ColorRole.Window, bg)
        palette.setColor(QPalette.ColorRole.Base, bg)
        editor.setPalette(palette)
        editor.setAutoFillBackground(True)

    def _commit_checkbox_editor(self, editor: QWidget) -> None:
        """Commit editor data when the user toggles the checkbox."""
        # Screenshot conceal / model reload can hide the editor while a queued
        # stateChanged still fires; Qt then warns the editor is not owned.
        if not editor.isVisible() or editor.parentWidget() is None:
            return
        self.commitData.emit(editor)
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Create a full-cell editor with a centered native checkbox and drink icon.

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        container = QWidget(parent)
        self._apply_editor_row_background(container, option)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        checkbox = QCheckBox(container)
        checkbox.setText("")
        install_drink_checkbox_icon(checkbox, size=DRINK_ICON_SIZE)
        checkbox.stateChanged.connect(lambda _state, editor=container: self._commit_checkbox_editor(editor))
        layout.addWidget(checkbox)

        container.setProperty("_is_drink_checkbox", checkbox)
        return container
```

</details>

### ⚙️ Method `displayText`

```python
def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str
```

Hide text; the drink marker is painted as a Lucide icon.

<details>
<summary>Code:</summary>

```python
def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        return ""
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw the colored coffee icon when the row is a drink.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else None
        if style is not None:
            style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)
        if not parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)):
            return
        icon = create_drink_icon(DRINK_ICON_SIZE)
        side = min(option.rect.width(), option.rect.height(), DRINK_ICON_SIZE + 4)
        icon.paint(
            painter,
            option.rect.x() + (option.rect.width() - side) // 2,
            option.rect.y() + (option.rect.height() - side) // 2,
            side,
            side,
        )
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None
```

Load model value into the checkbox editor.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        checkbox = _checkbox_from_editor(editor)
        if checkbox is None:
            return
        checkbox.blockSignals(True)  # noqa: FBT003
        try:
            checkbox.setChecked(parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)))
        finally:
            checkbox.blockSignals(False)  # noqa: FBT003
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None
```

Write checkbox state back to the model as 1 or empty.

<details>
<summary>Code:</summary>

```python
def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        checkbox = _checkbox_from_editor(editor)
        if checkbox is None:
            return
        model.setData(index, is_drink_to_model(checked=checkbox.isChecked()), Qt.ItemDataRole.EditRole)
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Keep the drink column wide enough for the coffee icon.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        hint = super().sizeHint(option, index)
        return QSize(max(hint.width(), DRINK_ICON_SIZE + 12), max(hint.height(), DRINK_ICON_SIZE + 8))
```

</details>

### ⚙️ Method `updateEditorGeometry`

```python
def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> None
```

Resize the editor to cover the entire table cell.

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

## 🔧 Function `is_drink_to_model`

```python
def is_drink_to_model(*, checked: bool) -> str
```

Convert checkbox state to food log model storage.

Args:

- `checked` (`bool`): Whether the drink checkbox is checked.

Returns:

- `str`: `1` when checked, empty string otherwise.

<details>
<summary>Code:</summary>

```python
def is_drink_to_model(*, checked: bool) -> str:
    return "1" if checked else ""
```

</details>

## 🔧 Function `parse_is_drink_cell`

```python
def parse_is_drink_cell(value: object) -> bool
```

Return whether a model cell value represents a drink.

Args:

- `value` (`object`): Raw cell value from the model.

Returns:

- `bool`: `True` if the value indicates a drink.

<details>
<summary>Code:</summary>

```python
def parse_is_drink_cell(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip().lower()
    if not text:
        return False
    return text in _TRUTHY_IS_DRINK or text == DRINK_EMOJI
```

</details>
