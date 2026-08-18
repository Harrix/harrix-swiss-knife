---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `choose_family_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ChooseIconFamilyDialog`](#%EF%B8%8F-class-chooseiconfamilydialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `selected_family`](#%EF%B8%8F-method-selected_family)

</details>

## 🏛️ Class `ChooseIconFamilyDialog`

```python
class ChooseIconFamilyDialog(QDialog)
```

Searchable list of icon families.

<details>
<summary>Code:</summary>

```python
class ChooseIconFamilyDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        *,
        catalog: IconCatalog,
        preferred_id: str | None = None,
    ) -> None:
        """Build the chooser for `catalog`."""
        super().__init__(parent)
        self._catalog = catalog
        self._preferred_id = preferred_id
        self.setWindowTitle("Choose icon for variants")
        self.setMinimumSize(480, 520)
        qt_modality.set_owner_window_modal(self)
        self._setup_ui()
        self._populate("")

    def selected_family(self) -> IconFamily | None:
        """Return the currently selected family."""
        item = self._list.currentItem()
        if item is None:
            return None
        family = item.data(Qt.ItemDataRole.UserRole)
        return family if family is not None else None

    def _on_filter_changed(self, text: str) -> None:
        self._populate(text)

    def _populate(self, query: str) -> None:
        self._list.clear()
        preferred_row = -1
        for family in self._catalog.filter_icons(query=query):
            item = QListWidgetItem(f"{family.title}  ({family.id})")
            item.setData(Qt.ItemDataRole.UserRole, family)
            self._list.addItem(item)
            if self._preferred_id and family.id == self._preferred_id:
                preferred_row = self._list.count() - 1
        if preferred_row >= 0:
            self._list.setCurrentRow(preferred_row)
        elif self._list.count():
            self._list.setCurrentRow(0)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select the icon that should receive the new variants:"))
        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Search by title, tags, id…")
        self._filter.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self._filter)
        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(lambda _item: self.accept())
        layout.addWidget(self._list, 1)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = make_emoji_push_button("Cancel", "❌")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        ok = make_emoji_push_button("OK", "✅")
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        buttons.addWidget(ok)
        layout.addLayout(buttons)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, *, catalog: IconCatalog, preferred_id: str | None = None) -> None
```

Build the chooser for `catalog`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        *,
        catalog: IconCatalog,
        preferred_id: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._catalog = catalog
        self._preferred_id = preferred_id
        self.setWindowTitle("Choose icon for variants")
        self.setMinimumSize(480, 520)
        qt_modality.set_owner_window_modal(self)
        self._setup_ui()
        self._populate("")
```

</details>

### ⚙️ Method `selected_family`

```python
def selected_family(self) -> IconFamily | None
```

Return the currently selected family.

<details>
<summary>Code:</summary>

```python
def selected_family(self) -> IconFamily | None:
        item = self._list.currentItem()
        if item is None:
            return None
        family = item.data(Qt.ItemDataRole.UserRole)
        return family if family is not None else None
```

</details>
