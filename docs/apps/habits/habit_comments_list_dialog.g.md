---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_comments_list_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HabitCommentsListDialog`](#%EF%B8%8F-class-habitcommentslistdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `chosen_date`](#%EF%B8%8F-method-chosen_date)

</details>

## 🏛️ Class `HabitCommentsListDialog`

```python
class HabitCommentsListDialog(QDialog)
```

Browse all comments for a habit and open one for editing.

<details>
<summary>Code:</summary>

```python
class HabitCommentsListDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        habit_name: str,
        comments: Sequence[HabitDayComment],
    ) -> None:
        """Initialize the comments list.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `habit_name` (`str`): Habit title shown in the window.
        - `comments` (`Sequence[HabitDayComment]`): Dated comments, newest first.

        """
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(f"Comments — {habit_name}")
        self.setMinimumWidth(460)
        self.resize(520, 420)
        self._chosen_date: str | None = None

        root = QVBoxLayout(self)
        hint = QLabel("Double-click a day to view or edit the comment.")
        hint.setStyleSheet("color: #6B7280; font-size: 12px;")
        root.addWidget(hint)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_item_activated)
        root.addWidget(self._list, 1)

        if not comments:
            empty = QListWidgetItem("No comments yet.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            self._list.addItem(empty)
        else:
            for item in comments:
                row = QListWidgetItem(f"{item.date}  {preview_habit_comment(item.text)}")
                row.setData(Qt.ItemDataRole.UserRole, item.date)
                self._list.addItem(row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        apply_emoji_dialog_buttons(buttons)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.reject)
        root.addWidget(buttons)

    def chosen_date(self) -> str | None:
        """Return the date selected for editing, if any."""
        return self._chosen_date

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        date_str = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(date_str, str) or not date_str:
            return
        self._chosen_date = date_str
        self.accept()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, habit_name: str, comments: Sequence[HabitDayComment]) -> None
```

Initialize the comments list.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- [`habit_name`](habit_edit_dialog.g.md#%EF%B8%8F-method-habit_name) (`str`): Habit title shown in the window.
- `comments` (`Sequence[HabitDayComment]`): Dated comments, newest first.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        habit_name: str,
        comments: Sequence[HabitDayComment],
    ) -> None:
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(f"Comments — {habit_name}")
        self.setMinimumWidth(460)
        self.resize(520, 420)
        self._chosen_date: str | None = None

        root = QVBoxLayout(self)
        hint = QLabel("Double-click a day to view or edit the comment.")
        hint.setStyleSheet("color: #6B7280; font-size: 12px;")
        root.addWidget(hint)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_item_activated)
        root.addWidget(self._list, 1)

        if not comments:
            empty = QListWidgetItem("No comments yet.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            self._list.addItem(empty)
        else:
            for item in comments:
                row = QListWidgetItem(f"{item.date}  {preview_habit_comment(item.text)}")
                row.setData(Qt.ItemDataRole.UserRole, item.date)
                self._list.addItem(row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        apply_emoji_dialog_buttons(buttons)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.reject)
        root.addWidget(buttons)
```

</details>

### ⚙️ Method `chosen_date`

```python
def chosen_date(self) -> str | None
```

Return the date selected for editing, if any.

<details>
<summary>Code:</summary>

```python
def chosen_date(self) -> str | None:
        return self._chosen_date
```

</details>
