---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `pinned_folders_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ManagePinnedFoldersDialog`](#%EF%B8%8F-class-managepinnedfoldersdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `accept`](#%EF%B8%8F-method-accept)
  - [⚙️ Method `saved_paths`](#%EF%B8%8F-method-saved_paths)

</details>

## 🏛️ Class `ManagePinnedFoldersDialog`

```python
class ManagePinnedFoldersDialog(QDialog)
```

Edit the `path_vector_icons_pinned` list used by File → Pinned folders.

<details>
<summary>Code:</summary>

```python
class ManagePinnedFoldersDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Load current pinned folders into an editable list."""
        super().__init__(parent)
        self.setWindowTitle("Manage pinned folders")
        self.setMinimumSize(560, 420)
        qt_modality.set_owner_window_modal(self)
        self._paths: list[Path] = list(load_pinned_folders())
        self._setup_ui()
        self._reload_list()

    def accept(self) -> None:
        """Persist the edited list, then close."""
        self._paths = save_pinned_folders(self._paths)
        super().accept()

    def saved_paths(self) -> list[Path]:
        """Return the paths last written on Accept."""
        return list(self._paths)

    def _on_add(self) -> None:
        start = str(self._paths[0]) if self._paths else ""
        chosen = QFileDialog.getExistingDirectory(self, "Add pinned folder", start)
        if not chosen:
            return
        path = Path(chosen)
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if not resolved.is_dir():
            QMessageBox.warning(self, "Pinned folders", f"Folder not found:\n{resolved}")
            return
        if any(item.resolve() == resolved for item in self._paths):
            QMessageBox.information(self, "Pinned folders", "That folder is already pinned.")
            return
        self._paths.append(resolved)
        self._reload_list()
        self._list.setCurrentRow(self._list.count() - 1)

    def _on_remove(self) -> None:
        row = self._list.currentRow()
        if row < 0 or row >= len(self._paths):
            return
        del self._paths[row]
        self._reload_list()
        if self._list.count():
            self._list.setCurrentRow(min(row, self._list.count() - 1))

    def _reload_list(self) -> None:
        self._list.clear()
        for path in self._paths:
            try:
                resolved = path.resolve()
            except OSError:
                resolved = path
            missing = "" if resolved.is_dir() else "  (missing)"
            item = QListWidgetItem(f"{resolved}{missing}")
            item.setData(Qt.ItemDataRole.UserRole, resolved)
            if missing:
                item.setForeground(Qt.GlobalColor.darkGray)
            self._list.addItem(item)
        self._remove_btn.setEnabled(self._list.count() > 0)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Pinned folders appear under File → Pinned folders and in the folder combobox."),
        )
        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self._list, stretch=1)

        buttons = QHBoxLayout()
        add_btn = make_lucide_push_button("Add…", "folder-plus")
        add_btn.clicked.connect(self._on_add)
        self._remove_btn = make_lucide_push_button("Remove", "trash")
        self._remove_btn.clicked.connect(self._on_remove)
        buttons.addWidget(add_btn)
        buttons.addWidget(self._remove_btn)
        buttons.addStretch(1)
        cancel_btn = make_lucide_push_button("Cancel", "x")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = make_lucide_push_button("Save", "check")
        style_accept_button(ok_btn)
        ok_btn.clicked.connect(self.accept)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Load current pinned folders into an editable list.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Manage pinned folders")
        self.setMinimumSize(560, 420)
        qt_modality.set_owner_window_modal(self)
        self._paths: list[Path] = list(load_pinned_folders())
        self._setup_ui()
        self._reload_list()
```

</details>

### ⚙️ Method `accept`

```python
def accept(self) -> None
```

Persist the edited list, then close.

<details>
<summary>Code:</summary>

```python
def accept(self) -> None:
        self._paths = save_pinned_folders(self._paths)
        super().accept()
```

</details>

### ⚙️ Method `saved_paths`

```python
def saved_paths(self) -> list[Path]
```

Return the paths last written on Accept.

<details>
<summary>Code:</summary>

```python
def saved_paths(self) -> list[Path]:
        return list(self._paths)
```

</details>
