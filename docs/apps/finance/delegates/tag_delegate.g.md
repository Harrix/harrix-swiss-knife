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
  - [⚙️ Method `tags (property)`](#%EF%B8%8F-method-tags-property)
  - [⚙️ Method `tags (setter)`](#%EF%B8%8F-method-tags-setter)
  - [⚙️ Method `updateEditorGeometry`](#%EF%B8%8F-method-updateeditorgeometry)

</details>

## 🏛️ Class `TagDelegate`

```python
class TagDelegate(QStyledItemDelegate)
```

Edit a transaction tag cell as a check list of several tags.

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
        """Open a check list of known tags with the current cell values checked."""
        raw = index.data()
        selected = parse_tag_text(str(raw) if raw is not None else "")
        return _TagCheckListEditor(self._known_tags(), selected, parent)

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Check the tags currently stored in the cell."""
        checklist = cast("_TagCheckListEditor", editor)
        raw = index.data()
        selected = {name.casefold() for name in parse_tag_text(str(raw) if raw is not None else "")}
        tag_list = checklist.findChild(QListWidget)
        if tag_list is None:
            return
        for row in range(tag_list.count()):
            item = tag_list.item(row)
            if item is None:
                continue
            item.setCheckState(Qt.CheckState.Checked if item.text().casefold() in selected else Qt.CheckState.Unchecked)

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
        """Give the check list enough height to show several tags."""
        rect = option.rect
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

- `parent` (`QObject | None`): Parent object, usually the transactions view.
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

Open a check list of known tags with the current cell values checked.

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
        selected = {name.casefold() for name in parse_tag_text(str(raw) if raw is not None else "")}
        tag_list = checklist.findChild(QListWidget)
        if tag_list is None:
            return
        for row in range(tag_list.count()):
            item = tag_list.item(row)
            if item is None:
                continue
            item.setCheckState(Qt.CheckState.Checked if item.text().casefold() in selected else Qt.CheckState.Unchecked)
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

Give the check list enough height to show several tags.

<details>
<summary>Code:</summary>

```python
def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        rect = option.rect
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
