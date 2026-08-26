---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_day_comment_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HabitDayCommentDialog`](#%EF%B8%8F-class-habitdaycommentdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `comment_text`](#%EF%B8%8F-method-comment_text)

</details>

## 🏛️ Class `HabitDayCommentDialog`

```python
class HabitDayCommentDialog(QDialog)
```

Edit the Markdown comment attached to one habit on one date.

<details>
<summary>Code:</summary>

```python
class HabitDayCommentDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        habit_name: str,
        date_str: str,
        text: str = "",
    ) -> None:
        """Initialize the comment dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `habit_name` (`str`): Habit title shown in the heading.
        - `date_str` (`str`): Day in `YYYY-MM-DD` format.
        - `text` (`str`): Current comment. Defaults to `""`.

        """
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(f"Comment — {habit_name} — {date_str}")
        self.setMinimumWidth(420)
        self.resize(480, 320)
        self._deleted = False

        root = QVBoxLayout(self)
        heading = QLabel(f"{habit_name} · {date_str}")
        heading.setStyleSheet("color: #111827; font-size: 14px; font-weight: 700;")
        root.addWidget(heading)

        self._edit = QPlainTextEdit(text)
        self._edit.setPlaceholderText("Write a comment for this day…")
        root.addWidget(self._edit, 1)

        buttons = QHBoxLayout()
        self._delete_button = make_emoji_push_button("Delete", DELETE_BUTTON_EMOJI)
        self._delete_button.setEnabled(bool(text.strip()))
        self._delete_button.clicked.connect(self._on_delete)
        buttons.addWidget(self._delete_button)
        buttons.addStretch(1)

        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(box)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        buttons.addWidget(box)
        root.addLayout(buttons)

        self._edit.setFocus()

    def comment_text(self) -> str:
        """Return the edited comment, empty when deleted or cleared."""
        if self._deleted:
            return ""
        return self._edit.toPlainText().strip()

    def _on_delete(self) -> None:
        reply = message_box.question(
            self,
            "Delete comment",
            "Delete this day's comment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._deleted = True
            self.accept()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, habit_name: str, date_str: str, text: str = '') -> None
```

Initialize the comment dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- [`habit_name`](habit_edit_dialog.g.md#%EF%B8%8F-method-habit_name) (`str`): Habit title shown in the heading.
- `date_str` (`str`): Day in `YYYY-MM-DD` format.
- `text` (`str`): Current comment. Defaults to `""`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        habit_name: str,
        date_str: str,
        text: str = "",
    ) -> None:
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(f"Comment — {habit_name} — {date_str}")
        self.setMinimumWidth(420)
        self.resize(480, 320)
        self._deleted = False

        root = QVBoxLayout(self)
        heading = QLabel(f"{habit_name} · {date_str}")
        heading.setStyleSheet("color: #111827; font-size: 14px; font-weight: 700;")
        root.addWidget(heading)

        self._edit = QPlainTextEdit(text)
        self._edit.setPlaceholderText("Write a comment for this day…")
        root.addWidget(self._edit, 1)

        buttons = QHBoxLayout()
        self._delete_button = make_emoji_push_button("Delete", DELETE_BUTTON_EMOJI)
        self._delete_button.setEnabled(bool(text.strip()))
        self._delete_button.clicked.connect(self._on_delete)
        buttons.addWidget(self._delete_button)
        buttons.addStretch(1)

        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(box)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        buttons.addWidget(box)
        root.addLayout(buttons)

        self._edit.setFocus()
```

</details>

### ⚙️ Method `comment_text`

```python
def comment_text(self) -> str
```

Return the edited comment, empty when deleted or cleared.

<details>
<summary>Code:</summary>

```python
def comment_text(self) -> str:
        if self._deleted:
            return ""
        return self._edit.toPlainText().strip()
```

</details>
