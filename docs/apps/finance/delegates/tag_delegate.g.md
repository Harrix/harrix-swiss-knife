---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tag_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TagCheckListEditor`](#%EF%B8%8F-class-tagchecklisteditor)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `set_selected_tags`](#%EF%B8%8F-method-set_selected_tags)
  - [⚙️ Method `tags_text`](#%EF%B8%8F-method-tags_text)
- [🏛️ Class `TagDelegate`](#%EF%B8%8F-class-tagdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `setEditorData`](#%EF%B8%8F-method-seteditordata)
  - [⚙️ Method `setModelData`](#%EF%B8%8F-method-setmodeldata)
  - [⚙️ Method `tags (property)`](#%EF%B8%8F-method-tags-property)
  - [⚙️ Method `tags (setter)`](#%EF%B8%8F-method-tags-setter)
  - [⚙️ Method `updateEditorGeometry`](#%EF%B8%8F-method-updateeditorgeometry)
- [🔧 Function `pick_transaction_tags`](#-function-pick_transaction_tags)

</details>

## 🏛️ Class `TagCheckListEditor`

```python
class TagCheckListEditor(QFrame)
```

Fluent popup: checkboxes for known tags, a new-tag field, OK and Close.

<details>
<summary>Code:</summary>

```python
class TagCheckListEditor(QFrame):

    accepted = Signal()
    rejected = Signal()

    def __init__(
        self,
        known_tags: list[str],
        selected: list[str],
        parent: QWidget | None = None,
    ) -> None:
        """Build the Fluent check list and the field used to type one more tag."""
        super().__init__(parent)
        self.setObjectName("financeTagEditor")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
        layout.setSpacing(SPACE_S)

        self._scroll = FluentScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._host = QWidget(self._scroll)
        self._host.setObjectName("financeTagEditorHost")
        self._checks_layout = QVBoxLayout(self._host)
        self._checks_layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        self._checks_layout.setSpacing(2)
        self._checks_layout.addStretch(1)
        self._scroll.setWidget(self._host)
        layout.addWidget(self._scroll, stretch=1)

        self._checks: list[FluentCheckBox] = []
        names = list(known_tags)
        selected_keys = {name.casefold() for name in selected}
        known_keys = {name.casefold() for name in names}
        for name in selected:
            if name.casefold() not in known_keys:
                names.append(name)
                known_keys.add(name.casefold())
        for name in names:
            box = FluentCheckBox(name, self._host)
            box.setChecked(name.casefold() in selected_keys)
            self._checks_layout.insertWidget(self._checks_layout.count() - 1, box)
            self._checks.append(box)

        self._new_tag = FluentLineEdit(self, placeholder="Add tag", clearable=True, compact=True)
        layout.addWidget(self._new_tag)

        buttons = QHBoxLayout()
        buttons.setSpacing(SPACE_S)
        self._ok_button = FluentPrimaryButton("OK", self)
        self._ok_button.setDefault(True)
        self._ok_button.setAutoDefault(True)
        self._close_button = FluentPushButton("Close", self)
        self._close_button.setAutoDefault(False)
        buttons.addWidget(self._ok_button, stretch=1)
        buttons.addWidget(self._close_button, stretch=1)
        layout.addLayout(buttons)

        self._ok_button.clicked.connect(self.accepted.emit)
        self._close_button.clicked.connect(self.rejected.emit)
        self._new_tag.returnPressed.connect(self.accepted.emit)
        # Shortcuts work while focus is on checkboxes / the add field.
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.rejected.emit)
        QShortcut(QKeySequence(Qt.Key.Key_Return), self, self.accepted.emit)
        QShortcut(QKeySequence(Qt.Key.Key_Enter), self, self.accepted.emit)
        self.setFocusProxy(self._new_tag if not self._checks else self._checks[0])

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """OK on Enter; Close on Escape when the frame itself has focus."""
        if event.key() == Qt.Key.Key_Escape:
            self.rejected.emit()
            event.accept()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.accepted.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint the Fluent popup surface behind the checklist."""
        del event
        palette = palette_for(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), fill, palette.popup_stroke, RADIUS_OVERLAY)
        painter.end()

    def set_selected_tags(self, selected: list[str]) -> None:
        """Sync checkbox states to `selected` without changing the offered names."""
        selected_keys = {name.casefold() for name in selected}
        for box in self._checks:
            box.setChecked(box.text().casefold() in selected_keys)

    def tags_text(self) -> str:
        """Return the checked names plus any tag still typed in the add field."""
        names = [box.text() for box in self._checks if box.isChecked()]
        names.extend(parse_tag_text(self._new_tag.text()))
        return format_tag_text(names)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, known_tags: list[str], selected: list[str], parent: QWidget | None = None) -> None
```

Build the Fluent check list and the field used to type one more tag.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        known_tags: list[str],
        selected: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("financeTagEditor")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
        layout.setSpacing(SPACE_S)

        self._scroll = FluentScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._host = QWidget(self._scroll)
        self._host.setObjectName("financeTagEditorHost")
        self._checks_layout = QVBoxLayout(self._host)
        self._checks_layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        self._checks_layout.setSpacing(2)
        self._checks_layout.addStretch(1)
        self._scroll.setWidget(self._host)
        layout.addWidget(self._scroll, stretch=1)

        self._checks: list[FluentCheckBox] = []
        names = list(known_tags)
        selected_keys = {name.casefold() for name in selected}
        known_keys = {name.casefold() for name in names}
        for name in selected:
            if name.casefold() not in known_keys:
                names.append(name)
                known_keys.add(name.casefold())
        for name in names:
            box = FluentCheckBox(name, self._host)
            box.setChecked(name.casefold() in selected_keys)
            self._checks_layout.insertWidget(self._checks_layout.count() - 1, box)
            self._checks.append(box)

        self._new_tag = FluentLineEdit(self, placeholder="Add tag", clearable=True, compact=True)
        layout.addWidget(self._new_tag)

        buttons = QHBoxLayout()
        buttons.setSpacing(SPACE_S)
        self._ok_button = FluentPrimaryButton("OK", self)
        self._ok_button.setDefault(True)
        self._ok_button.setAutoDefault(True)
        self._close_button = FluentPushButton("Close", self)
        self._close_button.setAutoDefault(False)
        buttons.addWidget(self._ok_button, stretch=1)
        buttons.addWidget(self._close_button, stretch=1)
        layout.addLayout(buttons)

        self._ok_button.clicked.connect(self.accepted.emit)
        self._close_button.clicked.connect(self.rejected.emit)
        self._new_tag.returnPressed.connect(self.accepted.emit)
        # Shortcuts work while focus is on checkboxes / the add field.
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.rejected.emit)
        QShortcut(QKeySequence(Qt.Key.Key_Return), self, self.accepted.emit)
        QShortcut(QKeySequence(Qt.Key.Key_Enter), self, self.accepted.emit)
        self.setFocusProxy(self._new_tag if not self._checks else self._checks[0])
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

OK on Enter; Close on Escape when the frame itself has focus.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.rejected.emit()
            event.accept()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.accepted.emit()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Paint the Fluent popup surface behind the checklist.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        del event
        palette = palette_for(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), fill, palette.popup_stroke, RADIUS_OVERLAY)
        painter.end()
```

</details>

### ⚙️ Method `set_selected_tags`

```python
def set_selected_tags(self, selected: list[str]) -> None
```

Sync checkbox states to `selected` without changing the offered names.

<details>
<summary>Code:</summary>

```python
def set_selected_tags(self, selected: list[str]) -> None:
        selected_keys = {name.casefold() for name in selected}
        for box in self._checks:
            box.setChecked(box.text().casefold() in selected_keys)
```

</details>

### ⚙️ Method `tags_text`

```python
def tags_text(self) -> str
```

Return the checked names plus any tag still typed in the add field.

<details>
<summary>Code:</summary>

```python
def tags_text(self) -> str:
        names = [box.text() for box in self._checks if box.isChecked()]
        names.extend(parse_tag_text(self._new_tag.text()))
        return format_tag_text(names)
```

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
        editor = TagCheckListEditor(self._known_tags(), selected, parent)
        editor.accepted.connect(lambda: self._commit_editor(editor))
        editor.rejected.connect(lambda: self._close_editor(editor, revert=True))
        return editor

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
        checklist = cast("TagCheckListEditor", editor)
        raw = index.data()
        checklist.set_selected_tags(parse_tag_text(str(raw) if raw is not None else ""))

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write the checked tags back as one comma-separated cell value."""
        checklist = cast("TagCheckListEditor", editor)
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

    def _close_editor(self, editor: QWidget, *, revert: bool) -> None:
        hint = (
            QAbstractItemDelegate.EndEditHint.RevertModelCache
            if revert
            else QAbstractItemDelegate.EndEditHint.SubmitModelCache
        )
        self.closeEditor.emit(editor, hint)

    def _commit_editor(self, editor: QWidget) -> None:
        self.commitData.emit(editor)
        self._close_editor(editor, revert=False)

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
        editor = TagCheckListEditor(self._known_tags(), selected, parent)
        editor.accepted.connect(lambda: self._commit_editor(editor))
        editor.rejected.connect(lambda: self._close_editor(editor, revert=True))
        return editor
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
        checklist = cast("TagCheckListEditor", editor)
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
        checklist = cast("TagCheckListEditor", editor)
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

## 🔧 Function `pick_transaction_tags`

```python
def pick_transaction_tags(anchor: QWidget, known_tags: list[str], selected: list[str]) -> str | None
```

Show the tag check-list as a popup under `anchor` and return chosen text, or `None`.

<details>
<summary>Code:</summary>

```python
def pick_transaction_tags(
    anchor: QWidget,
    known_tags: list[str],
    selected: list[str],
) -> str | None:
    popup = _TagPickerPopup(
        known_tags,
        selected,
        fluent=is_fluent_themed(anchor),
    )
    width = max(anchor.width(), _EDITOR_MIN_WIDTH)
    popup.resize(width, _POPUP_HEIGHT)
    _place_popup_under_anchor(popup, anchor)

    result: dict[str, object] = {"value": None}
    loop = QEventLoop(popup)

    def on_finished(value: object) -> None:
        result["value"] = value
        loop.quit()

    popup.finished.connect(on_finished)
    popup.show()
    popup.editor.setFocus(Qt.FocusReason.PopupFocusReason)
    loop.exec()
    popup.deleteLater()
    value = result["value"]
    return value if isinstance(value, str) else None
```

</details>
