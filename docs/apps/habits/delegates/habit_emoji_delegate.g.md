---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_emoji_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HabitEmojiDelegate`](#%EF%B8%8F-class-habitemojidelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)

</details>

## 🏛️ Class `HabitEmojiDelegate`

```python
class HabitEmojiDelegate(QStyledItemDelegate)
```

Delegate that edits emoji values through [`HabitEmojiPickerDialog`](../habit_emoji_picker_dialog.g.md#%EF%B8%8F-class-habitemojipickerdialog).

<details>
<summary>Code:</summary>

```python
class HabitEmojiDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize HabitEmojiDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.

        """
        super().__init__(parent)

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Open the picker on left-click or double-click."""
        if event.type() not in {QEvent.Type.MouseButtonDblClick, QEvent.Type.MouseButtonRelease}:
            return super().editorEvent(event, model, option, index)
        if not isinstance(event, QMouseEvent) or event.button() != Qt.MouseButton.LeftButton:
            return super().editorEvent(event, model, option, index)
        parent = option.widget
        self._pick_and_apply(parent.window() if parent is not None else None, model, index)
        return True

    def _pick_and_apply(
        self,
        parent: QWidget | None,
        model: QAbstractItemModel | None,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if model is None or not index.isValid():
            return
        current = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        dialog = HabitEmojiPickerDialog(parent, current_emoji=current)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        model.setData(index, normalize_habit_emoji(dialog.selected_emoji()), Qt.ItemDataRole.EditRole)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize HabitEmojiDelegate.

Args:

- `parent` (`QObject | None`): Parent object for the delegate.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Open the picker on left-click or double-click.

<details>
<summary>Code:</summary>

```python
def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if event.type() not in {QEvent.Type.MouseButtonDblClick, QEvent.Type.MouseButtonRelease}:
            return super().editorEvent(event, model, option, index)
        if not isinstance(event, QMouseEvent) or event.button() != Qt.MouseButton.LeftButton:
            return super().editorEvent(event, model, option, index)
        parent = option.widget
        self._pick_and_apply(parent.window() if parent is not None else None, model, index)
        return True
```

</details>
