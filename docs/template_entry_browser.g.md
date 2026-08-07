---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `template_entry_browser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TemplateEntryBrowserGroup`](#%EF%B8%8F-class-templateentrybrowsergroup)
- [🏛️ Class `TemplateEntryBrowserWidget`](#%EF%B8%8F-class-templateentrybrowserwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_selected_entry`](#%EF%B8%8F-method-get_selected_entry)
  - [⚙️ Method `set_groups`](#%EF%B8%8F-method-set_groups)
- [🏛️ Class `TemplateExistingEntry`](#%EF%B8%8F-class-templateexistingentry)

</details>

## 🏛️ Class `TemplateEntryBrowserGroup`

```python
class TemplateEntryBrowserGroup
```

Group of existing entries (city folder, year file, etc.).

<details>
<summary>Code:</summary>

```python
class TemplateEntryBrowserGroup:

    label: str
    entries: tuple[TemplateExistingEntry, ...]
```

</details>

## 🏛️ Class `TemplateEntryBrowserWidget`

```python
class TemplateEntryBrowserWidget(QWidget)
```

Left panel with filter and tree of existing entries plus Add new Entry.

<details>
<summary>Code:</summary>

```python
class TemplateEntryBrowserWidget(QWidget):

    selection_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize filter field and entry tree."""
        super().__init__(parent)
        self._groups: list[TemplateEntryBrowserGroup] = []
        self._selected_entry: TemplateExistingEntry | None = None
        self._setup_ui()

    def get_selected_entry(self) -> TemplateExistingEntry | None:
        """Return selected existing entry, or `None` when Add new Entry is selected."""
        return self._selected_entry

    def set_groups(self, groups: list[TemplateEntryBrowserGroup]) -> None:
        """Populate the tree from grouped existing entries."""
        self._groups = groups
        self._rebuild_tree()
        self._select_add_new_entry()

    def _apply_filter(self, text: str) -> None:
        needle = text.strip().casefold()

        def matches_item(item: QTreeWidgetItem) -> bool:
            role = item.data(0, Qt.ItemDataRole.UserRole)
            if role == ADD_NEW_ENTRY_ROLE:
                return True
            if not needle:
                return True
            if needle in item.text(0).casefold():
                return True
            return any(matches_item(item.child(index)) for index in range(item.childCount()))

        for index in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(index)
            if item is not None:
                item.setHidden(not matches_item(item))

    def _emit_selection(self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None) -> None:
        if current is None:
            self._selected_entry = None
            self.selection_changed.emit(None)
            return

        role = current.data(0, Qt.ItemDataRole.UserRole)
        if role == ADD_NEW_ENTRY_ROLE:
            self._selected_entry = None
            self.selection_changed.emit(None)
            return

        if isinstance(role, TemplateExistingEntry):
            self._selected_entry = role
            self.selection_changed.emit(role)
            return

        self._selected_entry = None
        self.selection_changed.emit(None)

    def _rebuild_tree(self) -> None:
        self._tree.clear()
        add_new_item = QTreeWidgetItem([ADD_NEW_ENTRY_LABEL])
        add_new_item.setData(0, Qt.ItemDataRole.UserRole, ADD_NEW_ENTRY_ROLE)
        self._tree.addTopLevelItem(add_new_item)

        for group in self._groups:
            group_item = QTreeWidgetItem([group.label])
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            for entry in group.entries:
                child = QTreeWidgetItem([entry.label])
                child.setData(0, Qt.ItemDataRole.UserRole, entry)
                group_item.addChild(child)
            self._tree.addTopLevelItem(group_item)
            group_item.setExpanded(True)

    def _select_add_new_entry(self) -> None:
        if self._tree.topLevelItemCount() > 0:
            first = self._tree.topLevelItem(0)
            if first is not None:
                self._tree.setCurrentItem(first)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._filter_edit = QLineEdit()
        self._filter_edit.setPlaceholderText("Filter entries…")
        self._filter_edit.textChanged.connect(self._apply_filter)
        layout.addWidget(self._filter_edit)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setMinimumWidth(240)
        self._tree.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._tree.currentItemChanged.connect(self._emit_selection)
        layout.addWidget(self._tree)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize filter field and entry tree.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._groups: list[TemplateEntryBrowserGroup] = []
        self._selected_entry: TemplateExistingEntry | None = None
        self._setup_ui()
```

</details>

### ⚙️ Method `get_selected_entry`

```python
def get_selected_entry(self) -> TemplateExistingEntry | None
```

Return selected existing entry, or `None` when Add new Entry is selected.

<details>
<summary>Code:</summary>

```python
def get_selected_entry(self) -> TemplateExistingEntry | None:
        return self._selected_entry
```

</details>

### ⚙️ Method `set_groups`

```python
def set_groups(self, groups: list[TemplateEntryBrowserGroup]) -> None
```

Populate the tree from grouped existing entries.

<details>
<summary>Code:</summary>

```python
def set_groups(self, groups: list[TemplateEntryBrowserGroup]) -> None:
        self._groups = groups
        self._rebuild_tree()
        self._select_add_new_entry()
```

</details>

## 🏛️ Class `TemplateExistingEntry`

```python
class TemplateExistingEntry
```

Reference to an existing Markdown entry that can be loaded into the template form.

<details>
<summary>Code:</summary>

```python
class TemplateExistingEntry:

    kind: Literal["city_note", "file_block"]
    label: str
    note_md: str | None = None
    target_path: str | None = None
    block_start: int | None = None
    block_end: int | None = None
    display_title: str | None = None
```

</details>
