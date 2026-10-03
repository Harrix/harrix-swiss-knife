---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `keyboard_shortcuts.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `KeyboardShortcutsDialog`](#%EF%B8%8F-class-keyboardshortcutsdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `set_entries`](#%EF%B8%8F-method-set_entries)
- [🏛️ Class `ShortcutHelpEntry`](#%EF%B8%8F-class-shortcuthelpentry)
- [🔧 Function `add_keyboard_shortcuts_help_action`](#-function-add_keyboard_shortcuts_help_action)
- [🔧 Function `collect_documented_shortcuts`](#-function-collect_documented_shortcuts)
- [🔧 Function `default_tracker_app_shortcut_help`](#-function-default_tracker_app_shortcut_help)
- [🔧 Function `install_documented_shortcut`](#-function-install_documented_shortcut)
- [🔧 Function `key_sequence_display`](#-function-key_sequence_display)
- [🔧 Function `merge_shortcut_help`](#-function-merge_shortcut_help)
- [🔧 Function `show_keyboard_shortcuts_help`](#-function-show_keyboard_shortcuts_help)
- [🔧 Function `sort_shortcut_help`](#-function-sort_shortcut_help)
- [🔧 Function `to_key_sequence`](#-function-to_key_sequence)

</details>

## 🏛️ Class `KeyboardShortcutsDialog`

```python
class KeyboardShortcutsDialog(QDialog)
```

Non-modal table of keyboard shortcuts that can stay open while using the app.

<details>
<summary>Code:</summary>

```python
class KeyboardShortcutsDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        *,
        title: str,
        entries: list[ShortcutHelpEntry],
    ) -> None:
        """Build the help window."""
        super().__init__(parent)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self.setWindowTitle(title)
        self.setMinimumSize(520, 360)
        self.resize(640, 480)

        root = QVBoxLayout(self)
        hint = QLabel("This window is non-modal — keep it open while you work.", self)
        hint.setWordWrap(True)
        root.addWidget(hint)

        self._filter = QLineEdit(self)
        self._filter.setPlaceholderText("Search keys or actions…")
        install_line_edit_search_chrome(self._filter, clear_tooltip="Clear search")
        self._filter.textChanged.connect(self._apply_filter)
        root.addWidget(self._filter)

        self._table = QTableWidget(0, 3, self)
        self._table.setHorizontalHeaderLabels(["Category", "Shortcut", "Action"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        root.addWidget(self._table, stretch=1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_btn = QPushButton("Close", self)
        close_btn.setIcon(create_lucide_icon("x", 16))
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

        self._entries: list[ShortcutHelpEntry] = []
        self.set_entries(entries)

    def set_entries(self, entries: list[ShortcutHelpEntry]) -> None:
        """Replace the shortcut list and refresh the table."""
        self._entries = sort_shortcut_help(list(entries))
        self._apply_filter(self._filter.text())

    def _apply_filter(self, text: str) -> None:
        needle = text.strip().casefold()
        rows = [
            entry
            for entry in self._entries
            if not needle
            or needle in entry.category.casefold()
            or needle in entry.keys.casefold()
            or needle in entry.description.casefold()
        ]
        self._table.setRowCount(len(rows))
        for row, entry in enumerate(rows):
            self._table.setItem(row, 0, QTableWidgetItem(entry.category))
            self._table.setItem(row, 1, QTableWidgetItem(entry.keys))
            self._table.setItem(row, 2, QTableWidgetItem(entry.description))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, *, title: str, entries: list[ShortcutHelpEntry]) -> None
```

Build the help window.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        *,
        title: str,
        entries: list[ShortcutHelpEntry],
    ) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self.setWindowTitle(title)
        self.setMinimumSize(520, 360)
        self.resize(640, 480)

        root = QVBoxLayout(self)
        hint = QLabel("This window is non-modal — keep it open while you work.", self)
        hint.setWordWrap(True)
        root.addWidget(hint)

        self._filter = QLineEdit(self)
        self._filter.setPlaceholderText("Search keys or actions…")
        install_line_edit_search_chrome(self._filter, clear_tooltip="Clear search")
        self._filter.textChanged.connect(self._apply_filter)
        root.addWidget(self._filter)

        self._table = QTableWidget(0, 3, self)
        self._table.setHorizontalHeaderLabels(["Category", "Shortcut", "Action"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        root.addWidget(self._table, stretch=1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_btn = QPushButton("Close", self)
        close_btn.setIcon(create_lucide_icon("x", 16))
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

        self._entries: list[ShortcutHelpEntry] = []
        self.set_entries(entries)
```

</details>

### ⚙️ Method `set_entries`

```python
def set_entries(self, entries: list[ShortcutHelpEntry]) -> None
```

Replace the shortcut list and refresh the table.

<details>
<summary>Code:</summary>

```python
def set_entries(self, entries: list[ShortcutHelpEntry]) -> None:
        self._entries = sort_shortcut_help(list(entries))
        self._apply_filter(self._filter.text())
```

</details>

## 🏛️ Class `ShortcutHelpEntry`

```python
class ShortcutHelpEntry
```

One row in the keyboard-shortcuts help window.

<details>
<summary>Code:</summary>

```python
class ShortcutHelpEntry:

    keys: str
    description: str
    category: str = "General"
```

</details>

## 🔧 Function `add_keyboard_shortcuts_help_action`

```python
def add_keyboard_shortcuts_help_action(menu: Any, parent: QWidget, *, before: QAction | None = None, slot: Callable[[], None]) -> QAction
```

Insert a Help → Keyboard shortcuts action and return it.

<details>
<summary>Code:</summary>

```python
def add_keyboard_shortcuts_help_action(
    menu: Any,
    parent: QWidget,
    *,
    before: QAction | None = None,
    slot: Callable[[], None],
) -> QAction:
    action = QAction("Keyboard shortcuts", parent)
    apply_lucide_action_icon(action, "keyboard")
    action.triggered.connect(slot)
    if before is not None:
        menu.insertAction(before, action)
    else:
        menu.addAction(action)
    return action
```

</details>

## 🔧 Function `collect_documented_shortcuts`

```python
def collect_documented_shortcuts(widget: QWidget) -> list[ShortcutHelpEntry]
```

Collect help rows from `QShortcut` children that have `whatsThis` descriptions.

<details>
<summary>Code:</summary>

```python
def collect_documented_shortcuts(widget: QWidget) -> list[ShortcutHelpEntry]:
    entries: list[ShortcutHelpEntry] = []
    for shortcut in widget.findChildren(QShortcut):
        description = shortcut.whatsThis().strip()
        if not description:
            continue
        category = str(shortcut.property(_CATEGORY_PROPERTY) or "").strip() or "General"
        keys = key_sequence_display(shortcut.key())
        if not keys:
            continue
        entries.append(ShortcutHelpEntry(keys=keys, description=description, category=category))
    return merge_shortcut_help(entries)
```

</details>

## 🔧 Function `default_tracker_app_shortcut_help`

```python
def default_tracker_app_shortcut_help() -> list[ShortcutHelpEntry]
```

Shared shortcuts for Finance / Food / Fitness / Habits main Windows.

<details>
<summary>Code:</summary>

```python
def default_tracker_app_shortcut_help() -> list[ShortcutHelpEntry]:
    return [
        ShortcutHelpEntry("Ctrl+C", "Copy selected table cells to the clipboard", "Tables"),
        ShortcutHelpEntry("Enter", "Activate Add when an add control is focused", "Forms"),
        ShortcutHelpEntry("F1", "Show this keyboard shortcuts help", "Help"),
    ]
```

</details>

## 🔧 Function `install_documented_shortcut`

```python
def install_documented_shortcut(parent: QWidget, sequence: QKeySequence | QKeySequence.StandardKey | str, slot: Callable[[], None], *, description: str, category: str = 'General', registry: list[ShortcutHelpEntry] | None = None, context: Qt.ShortcutContext = Qt.ShortcutContext.WindowShortcut) -> QShortcut
```

Create a `QShortcut`, store help metadata on it, and optionally append to `registry`.

<details>
<summary>Code:</summary>

```python
def install_documented_shortcut(
    parent: QWidget,
    sequence: QKeySequence | QKeySequence.StandardKey | str,
    slot: Callable[[], None],
    *,
    description: str,
    category: str = "General",
    registry: list[ShortcutHelpEntry] | None = None,
    context: Qt.ShortcutContext = Qt.ShortcutContext.WindowShortcut,
) -> QShortcut:
    key_seq = to_key_sequence(sequence)
    shortcut = QShortcut(key_seq, parent)
    shortcut.setContext(context)
    shortcut.activated.connect(slot)
    shortcut.setWhatsThis(description)
    shortcut.setProperty(_CATEGORY_PROPERTY, category)
    if registry is not None:
        registry.append(
            ShortcutHelpEntry(
                keys=key_sequence_display(key_seq),
                description=description,
                category=category,
            ),
        )
    return shortcut
```

</details>

## 🔧 Function `key_sequence_display`

```python
def key_sequence_display(sequence: QKeySequence | QKeySequence.StandardKey | str) -> str
```

Return a readable shortcut string for help tables.

<details>
<summary>Code:</summary>

```python
def key_sequence_display(sequence: QKeySequence | QKeySequence.StandardKey | str) -> str:
    if isinstance(sequence, QKeySequence.StandardKey):
        bindings = QKeySequence.keyBindings(sequence)
        if bindings:
            return bindings[0].toString(QKeySequence.SequenceFormat.NativeText)
        return QKeySequence(sequence).toString(QKeySequence.SequenceFormat.NativeText)
    if isinstance(sequence, str):
        return QKeySequence(sequence).toString(QKeySequence.SequenceFormat.NativeText)
    text = sequence.toString(QKeySequence.SequenceFormat.NativeText).strip()
    return text or sequence.toString(QKeySequence.SequenceFormat.PortableText)
```

</details>

## 🔧 Function `merge_shortcut_help`

```python
def merge_shortcut_help(*groups: list[ShortcutHelpEntry]) -> list[ShortcutHelpEntry]
```

Merge groups, dropping duplicate (category, keys, description) rows.

<details>
<summary>Code:</summary>

```python
def merge_shortcut_help(*groups: list[ShortcutHelpEntry]) -> list[ShortcutHelpEntry]:
    seen: set[tuple[str, str, str]] = set()
    merged: list[ShortcutHelpEntry] = []
    for group in groups:
        for entry in group:
            key = (entry.category, entry.keys.casefold(), entry.description.casefold())
            if key in seen:
                continue
            seen.add(key)
            merged.append(entry)
    return merged
```

</details>

## 🔧 Function `show_keyboard_shortcuts_help`

```python
def show_keyboard_shortcuts_help(parent: QWidget | None, title: str, entries: list[ShortcutHelpEntry]) -> KeyboardShortcutsDialog
```

Show or raise a non-modal shortcuts window for `parent`.

<details>
<summary>Code:</summary>

```python
def show_keyboard_shortcuts_help(
    parent: QWidget | None,
    title: str,
    entries: list[ShortcutHelpEntry],
) -> KeyboardShortcutsDialog:
    owner = parent if isinstance(parent, QWidget) else None
    if owner is not None:
        existing = _open_help_dialogs.get(owner)
        if existing is not None and isValid(existing):
            existing.set_entries(entries)
            existing.setWindowTitle(title)
            existing.show()
            existing.raise_()
            existing.activateWindow()
            return existing

    dialog = KeyboardShortcutsDialog(owner, title=title, entries=entries)
    if owner is not None:
        _open_help_dialogs[owner] = dialog

        def _forget(_obj: object = None, *, forgotten: QWidget = owner) -> None:
            current = _open_help_dialogs.get(forgotten)
            if current is dialog:
                _open_help_dialogs.pop(forgotten, None)

        dialog.destroyed.connect(_forget)
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    return dialog
```

</details>

## 🔧 Function `sort_shortcut_help`

```python
def sort_shortcut_help(entries: list[ShortcutHelpEntry]) -> list[ShortcutHelpEntry]
```

Sort by category, then keys, then description.

<details>
<summary>Code:</summary>

```python
def sort_shortcut_help(entries: list[ShortcutHelpEntry]) -> list[ShortcutHelpEntry]:
    return sorted(
        entries, key=lambda item: (item.category.casefold(), item.keys.casefold(), item.description.casefold())
    )
```

</details>

## 🔧 Function `to_key_sequence`

```python
def to_key_sequence(sequence: QKeySequence | QKeySequence.StandardKey | str) -> QKeySequence
```

Normalize supported sequence forms to `QKeySequence`.

<details>
<summary>Code:</summary>

```python
def to_key_sequence(sequence: QKeySequence | QKeySequence.StandardKey | str) -> QKeySequence:
    if isinstance(sequence, QKeySequence.StandardKey):
        return QKeySequence(sequence)
    if isinstance(sequence, str):
        return QKeySequence(sequence)
    return sequence
```

</details>
