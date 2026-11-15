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

Delegate that edits emoji and Lucide through [`HabitIconEditDialog`](../habit_icon_edit_dialog.g.md#%EF%B8%8F-class-habiticoneditdialog).

<details>
<summary>Code:</summary>

```python
class HabitEmojiDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject | None = None, *, app_config: dict[str, Any] | None = None) -> None:
        """Initialize HabitEmojiDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.
        - `app_config` (`dict[str, Any] | None`): App config for Lucide AI suggestions.

        """
        super().__init__(parent)
        self._app_config = app_config or {}

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Open the icon editor on left-click or double-click."""
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
        current_emoji = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        current_lucide = normalize_habit_lucide_name(str(index.data(HABIT_ICON_LUCIDE_ROLE) or ""))
        habit_name = str(model.data(model.index(index.row(), 0), Qt.ItemDataRole.DisplayRole) or "")
        habit_id = _habit_id_from_index(model, index)

        dialog = HabitIconEditDialog(
            parent,
            emoji=current_emoji,
            icon_lucide=current_lucide,
            habit_name=habit_name,
            habit_id=habit_id,
            app_config=self._app_config,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        emoji = normalize_habit_emoji(dialog.selected_emoji(), habit_id=habit_id)
        lucide = dialog.selected_icon_lucide()
        icon = habit_lucide_icon(lucide)
        # UserRole / DecorationRole do not auto-save; EditRole does and reads Lucide from UserRole.
        model.setData(index, lucide, HABIT_ICON_LUCIDE_ROLE)
        model.setData(index, emoji, Qt.ItemDataRole.EditRole)
        model.setData(index, icon if not icon.isNull() else QIcon(), Qt.ItemDataRole.DecorationRole)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, *, app_config: dict[str, Any] | None = None) -> None
```

Initialize HabitEmojiDelegate.

Args:

- `parent` (`QObject | None`): Parent object for the delegate.
- `app_config` (`dict[str, Any] | None`): App config for Lucide AI suggestions.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None, *, app_config: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self._app_config = app_config or {}
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Open the icon editor on left-click or double-click.

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
