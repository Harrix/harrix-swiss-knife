---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_icon_edit_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HabitIconEditDialog`](#%EF%B8%8F-class-habiticoneditdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `selected_emoji`](#%EF%B8%8F-method-selected_emoji)
  - [⚙️ Method `selected_icon_lucide`](#%EF%B8%8F-method-selected_icon_lucide)

</details>

## 🏛️ Class `HabitIconEditDialog`

```python
class HabitIconEditDialog(QDialog)
```

Choose emoji and optional Lucide icon for a habit.

<details>
<summary>Code:</summary>

```python
class HabitIconEditDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        emoji: str = "",
        icon_lucide: str = "",
        habit_name: str = "",
        habit_id: int | None = None,
        app_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the icon editor.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `emoji` (`str`): Current emoji.
        - `icon_lucide` (`str`): Current Lucide ID.
        - `habit_name` (`str`): Habit name used as AI suggest query.
        - `habit_id` (`int | None`): Habit ID for emoji fallback.
        - `app_config` (`dict[str, Any] | None`): App config for Lucide AI.

        """
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle("Edit Habit Icon")
        self.setMinimumWidth(440)
        self._habit_id = habit_id
        self._habit_name = habit_name.strip()
        self._emoji = normalize_habit_emoji(emoji, habit_id=habit_id)
        self._app_config = app_config if app_config is not None else h.dev.config_load(get_config_path_str())
        self._bothub_state = BothubRequestState()

        root = QVBoxLayout(self)
        form = QFormLayout()

        emoji_row = QHBoxLayout()
        self._emoji_preview = QPushButton(self._emoji)
        self._emoji_preview.setFixedSize(44, 44)
        self._emoji_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self._emoji_preview.setStyleSheet("QPushButton { font-size: 22px; }")
        self._emoji_preview.setToolTip("Choose emoji")
        self._emoji_preview.clicked.connect(self._choose_emoji)
        choose_button = QPushButton("Choose…")
        choose_button.clicked.connect(self._choose_emoji)
        emoji_row.addWidget(self._emoji_preview)
        emoji_row.addWidget(choose_button)
        emoji_row.addStretch(1)
        form.addRow("Emoji:", emoji_row)

        self._lucide_row = LucideChoiceRow(
            self,
            current_name=normalize_habit_lucide_name(icon_lucide),
            presets=HABIT_LUCIDE_PRESETS,
            allow_empty=True,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            suggest_query_provider=lambda: self._habit_name,
        )
        form.addRow("Lucide:", self._lucide_row)
        root.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_lucide_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def selected_emoji(self) -> str:
        """Return the selected emoji."""
        return normalize_habit_emoji(self._emoji, habit_id=self._habit_id)

    def selected_icon_lucide(self) -> str:
        """Return the selected Lucide ID (empty when cleared)."""
        return normalize_habit_lucide_name(self._lucide_row.lucide_name())

    def _choose_emoji(self) -> None:
        dialog = HabitEmojiPickerDialog(self, current_emoji=self._emoji)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._emoji = dialog.selected_emoji() or (HABIT_EMOJI_PRESETS[0] if HABIT_EMOJI_PRESETS else "✅")
        self._emoji_preview.setText(self._emoji)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, emoji: str = '', icon_lucide: str = '', habit_name: str = '', habit_id: int | None = None, app_config: dict[str, Any] | None = None) -> None
```

Initialize the icon editor.

Args:

- `parent` (`QWidget | None`): Parent widget.
- [`emoji`](../common/emoji_picker_dialog.g.md#%EF%B8%8F-method-emoji) (`str`): Current emoji.
- `icon_lucide` (`str`): Current Lucide ID.
- [`habit_name`](habit_edit_dialog.g.md#%EF%B8%8F-method-habit_name) (`str`): Habit name used as AI suggest query.
- [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) (`int | None`): Habit ID for emoji fallback.
- `app_config` (`dict[str, Any] | None`): App config for Lucide AI.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        emoji: str = "",
        icon_lucide: str = "",
        habit_name: str = "",
        habit_id: int | None = None,
        app_config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle("Edit Habit Icon")
        self.setMinimumWidth(440)
        self._habit_id = habit_id
        self._habit_name = habit_name.strip()
        self._emoji = normalize_habit_emoji(emoji, habit_id=habit_id)
        self._app_config = app_config if app_config is not None else h.dev.config_load(get_config_path_str())
        self._bothub_state = BothubRequestState()

        root = QVBoxLayout(self)
        form = QFormLayout()

        emoji_row = QHBoxLayout()
        self._emoji_preview = QPushButton(self._emoji)
        self._emoji_preview.setFixedSize(44, 44)
        self._emoji_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self._emoji_preview.setStyleSheet("QPushButton { font-size: 22px; }")
        self._emoji_preview.setToolTip("Choose emoji")
        self._emoji_preview.clicked.connect(self._choose_emoji)
        choose_button = QPushButton("Choose…")
        choose_button.clicked.connect(self._choose_emoji)
        emoji_row.addWidget(self._emoji_preview)
        emoji_row.addWidget(choose_button)
        emoji_row.addStretch(1)
        form.addRow("Emoji:", emoji_row)

        self._lucide_row = LucideChoiceRow(
            self,
            current_name=normalize_habit_lucide_name(icon_lucide),
            presets=HABIT_LUCIDE_PRESETS,
            allow_empty=True,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            suggest_query_provider=lambda: self._habit_name,
        )
        form.addRow("Lucide:", self._lucide_row)
        root.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_lucide_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
```

</details>

### ⚙️ Method `selected_emoji`

```python
def selected_emoji(self) -> str
```

Return the selected emoji.

<details>
<summary>Code:</summary>

```python
def selected_emoji(self) -> str:
        return normalize_habit_emoji(self._emoji, habit_id=self._habit_id)
```

</details>

### ⚙️ Method `selected_icon_lucide`

```python
def selected_icon_lucide(self) -> str
```

Return the selected Lucide ID (empty when cleared).

<details>
<summary>Code:</summary>

```python
def selected_icon_lucide(self) -> str:
        return normalize_habit_lucide_name(self._lucide_row.lucide_name())
```

</details>
