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
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)
  - [⚙️ Method `tags (property)`](#%EF%B8%8F-method-tags-property)
  - [⚙️ Method `tags (setter)`](#%EF%B8%8F-method-tags-setter)
  - [⚙️ Method `updateEditorGeometry`](#%EF%B8%8F-method-updateeditorgeometry)

</details>

## 🏛️ Class `TagDelegate`

```python
class TagDelegate(QStyledItemDelegate)
```

Paint tags as Fluent chips and edit them with a check list.

<details>
<summary>Code:</summary>

```python
class TagDelegate(QStyledItemDelegate):

    def __init__(
        self,
        parent: QObject | None = None,
        tags: list[str] | None = None,
        *,
        tags_provider: Callable[[], list[str]] | None = None,
    ) -> None:
        """Initialize the tag delegate.

        Args:

        - `parent` (`QObject | None`): Parent object, usually the transactions view.
        - `tags` (`list[str] | None`): Fallback names when `tags_provider` is omitted.
        - `tags_provider` (`Callable[[], list[str]] | None`): Called each time the
          editor opens so newly saved tags appear without rebuilding the delegate.

        """
        super().__init__(parent)
        self._tags = list(tags or [])
        self._tags_provider = tags_provider

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Open a Fluent check list of known tags with the current cell values checked."""
        raw = index.data()
        selected = parse_tag_text(str(raw) if raw is not None else "")
        return _TagCheckListEditor(self._known_tags(), selected, parent)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw soft accent chips instead of plain comma-separated text."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        widget = opt.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)
        else:
            super().paint(painter, opt, index)

        raw = index.data()
        names = parse_tag_text(str(raw) if raw is not None else "")
        if not names:
            return
        _paint_tag_chips(painter, opt.rect, names, palette_for(widget))

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Check the tags currently stored in the cell."""
        checklist = cast("_TagCheckListEditor", editor)
        raw = index.data()
        checklist.set_selected_tags(parse_tag_text(str(raw) if raw is not None else ""))

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write the checked tags back as one comma-separated cell value."""
        checklist = cast("_TagCheckListEditor", editor)
        model.setData(index, checklist.tags_text(), Qt.ItemDataRole.DisplayRole)

    @property
    def tags(self) -> list[str]:
        """Tag names shown when no provider is set."""
        return list(self._tags)

    @tags.setter
    def tags(self, value: list[str] | None) -> None:
        self._tags = list(value or [])

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Place a Fluent-sized popup over the cell without clipping off-screen."""
        rect = QRect(option.rect)
        height = _EDITOR_HEIGHT
        width = max(rect.width(), _EDITOR_MIN_WIDTH)
        parent = editor.parentWidget()
        if parent is not None:
            bounds = parent.rect()
            width = min(width, bounds.width())
            height = min(height, bounds.height())
            if rect.top() + height > bounds.bottom() + 1:
                rect.moveTop(max(bounds.top(), bounds.bottom() + 1 - height))
            if rect.left() + width > bounds.right() + 1:
                rect.moveLeft(max(bounds.left(), bounds.right() + 1 - width))
        rect.setWidth(width)
        rect.setHeight(height)
        editor.setGeometry(rect)

    def _known_tags(self) -> list[str]:
        """Return the tag names the editor should offer."""
        if self._tags_provider is not None:
            return list(self._tags_provider())
        return list(self._tags)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, tags: list[str] | None = None, *, tags_provider: Callable[[], list[str]] | None = None) -> None
```

Initialize the tag delegate.

Args:

- [`parent`](../transaction_day_headers.g.md#%EF%B8%8F-method-parent) (`QObject | None`): Parent object, usually the transactions view.
- `tags` (`list[str] | None`): Fallback names when `tags_provider` is omitted.
- `tags_provider` (`Callable[[], list[str]] | None`): Called each time the
  editor opens so newly saved tags appear without rebuilding the delegate.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QObject | None = None,
        tags: list[str] | None = None,
        *,
        tags_provider: Callable[[], list[str]] | None = None,
    ) -> None:
        super().__init__(parent)
        self._tags = list(tags or [])
        self._tags_provider = tags_provider
```

</details>

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QWidget, _option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget
```

Open a Fluent check list of known tags with the current cell values checked.

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        raw = index.data()
        selected = parse_tag_text(str(raw) if raw is not None else "")
        return _TagCheckListEditor(self._known_tags(), selected, parent)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw soft accent chips instead of plain comma-separated text.

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
        opt.text = ""
        widget = opt.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)
        else:
            super().paint(painter, opt, index)

        raw = index.data()
        names = parse_tag_text(str(raw) if raw is not None else "")
        if not names:
            return
        _paint_tag_chips(painter, opt.rect, names, palette_for(widget))
```

</details>

### ⚙️ Method `setEditorData`

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None
```

Check the tags currently stored in the cell.

<details>
<summary>Code:</summary>

```python
def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        checklist = cast("_TagCheckListEditor", editor)
        raw = index.data()
        checklist.set_selected_tags(parse_tag_text(str(raw) if raw is not None else ""))
```

</details>

### ⚙️ Method `setModelData`

```python
def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None
```

Write the checked tags back as one comma-separated cell value.

<details>
<summary>Code:</summary>

```python
def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        checklist = cast("_TagCheckListEditor", editor)
        model.setData(index, checklist.tags_text(), Qt.ItemDataRole.DisplayRole)
```

</details>

### ⚙️ Method `tags (property)`

```python
def tags(self) -> list[str]
```

Tag names shown when no provider is set.

<details>
<summary>Code:</summary>

```python
def tags(self) -> list[str]:
        return list(self._tags)
```

</details>

### ⚙️ Method `tags (setter)`

```python
def tags(self, value: list[str] | None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def tags(self, value: list[str] | None) -> None:
        self._tags = list(value or [])
```

</details>

### ⚙️ Method `updateEditorGeometry`

```python
def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> None
```

Place a Fluent-sized popup over the cell without clipping off-screen.

<details>
<summary>Code:</summary>

```python
def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        rect = QRect(option.rect)
        height = _EDITOR_HEIGHT
        width = max(rect.width(), _EDITOR_MIN_WIDTH)
        parent = editor.parentWidget()
        if parent is not None:
            bounds = parent.rect()
            width = min(width, bounds.width())
            height = min(height, bounds.height())
            if rect.top() + height > bounds.bottom() + 1:
                rect.moveTop(max(bounds.top(), bounds.bottom() + 1 - height))
            if rect.left() + width > bounds.right() + 1:
                rect.moveLeft(max(bounds.left(), bounds.right() + 1 - width))
        rect.setWidth(width)
        rect.setHeight(height)
        editor.setGeometry(rect)
```

</details>
