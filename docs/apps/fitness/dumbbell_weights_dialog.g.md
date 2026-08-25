---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dumbbell_weights_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DumbbellWeightsDialog`](#%EF%B8%8F-class-dumbbellweightsdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `drafts`](#%EF%B8%8F-method-drafts)

</details>

## 🏛️ Class `DumbbellWeightsDialog`

```python
class DumbbellWeightsDialog(QDialog)
```

Add, rename, and delete template dumbbell weight values.

<details>
<summary>Code:</summary>

```python
class DumbbellWeightsDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        drafts: list[WeightDraft],
        *,
        used_names: set[str],
    ) -> None:
        """Build the editor for `drafts`.

        Args:

        - `parent` (`QWidget | None`): Owner window.
        - `drafts` (`list[WeightDraft]`): Current template weights.
        - `used_names` (`set[str]`): Weight names that appear in any set.

        """
        super().__init__(parent)
        self._used_names = {name.casefold() for name in used_names}
        self.setWindowTitle("Edit dumbbell weights")
        qt_modality.set_owner_window_modal(self)
        self.resize(420, 460)
        self._setup_ui()
        for draft in drafts:
            self._add_item(draft)

    def drafts(self) -> list[WeightDraft]:
        """Return the edited weight rows."""
        result: list[WeightDraft] = []
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is None:
                continue
            original = item.data(_ORIGINAL_NAME_ROLE)
            result.append(
                WeightDraft(
                    original_name=str(original) if original else None,
                    name=item.text().strip(),
                    calories_modifier=float(item.data(_CALORIES_ROLE) or 1.0),
                    name_local=str(item.data(_NAME_LOCAL_ROLE) or ""),
                )
            )
        return result

    def _add_item(self, draft: WeightDraft) -> QListWidgetItem:
        item = QListWidgetItem(draft.name)
        item.setData(_USED_ROLE, self._is_used(draft.original_name or draft.name))
        item.setData(_ORIGINAL_NAME_ROLE, draft.original_name or "")
        item.setData(_CALORIES_ROLE, draft.calories_modifier)
        item.setData(_NAME_LOCAL_ROLE, draft.name_local)
        self._list.addItem(item)
        return item

    def _current_item(self) -> QListWidgetItem | None:
        return self._list.currentItem()

    def _is_used(self, name: str) -> bool:
        return name.strip().casefold() in self._used_names

    def _on_add(self) -> None:
        text, ok = QInputDialog.getText(self, "Add dumbbell weight", "Weight:")
        if not ok:
            return
        name = text.strip()
        if not name:
            return
        item = self._add_item(WeightDraft(original_name=None, name=name))
        self._list.setCurrentItem(item)

    def _on_delete(self) -> None:
        item = self._current_item()
        if item is None:
            return
        if bool(item.data(_USED_ROLE)):
            message_box.warning(
                self,
                "Cannot delete weight",
                f"'{item.text()}' is used in at least one set and cannot be deleted.",
            )
            return
        row = self._list.row(item)
        self._list.takeItem(row)

    def _on_rename(self) -> None:
        item = self._current_item()
        if item is None:
            return
        text, ok = QInputDialog.getText(self, "Rename dumbbell weight", "Weight:", text=item.text())
        if not ok:
            return
        name = text.strip()
        if not name:
            return
        item.setText(name)

    def _on_selection_changed(self) -> None:
        item = self._current_item()
        self._delete_button.setEnabled(item is not None and not bool(item.data(_USED_ROLE)))
        self._rename_button.setEnabled(item is not None)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                f"Possible dumbbell weights from '{DUMBBELL_WEIGHT_TEMPLATE_EXERCISE}'. "
                "OK saves the list and syncs it to other dumbbell exercises.",
                self,
            )
        )
        self._list = QListWidget(self)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.itemDoubleClicked.connect(lambda _item: self._on_rename())
        self._list.currentItemChanged.connect(lambda *_args: self._on_selection_changed())
        layout.addWidget(self._list, 1)

        row = QHBoxLayout()
        self._add_button = make_emoji_push_button("Add", "➕")  # noqa: RUF001
        self._rename_button = make_emoji_push_button("Rename", "✏️")
        self._delete_button = make_emoji_push_button("Delete", "🗑️")
        self._add_button.clicked.connect(self._on_add)
        self._rename_button.clicked.connect(self._on_rename)
        self._delete_button.clicked.connect(self._on_delete)
        row.addWidget(self._add_button)
        row.addWidget(self._rename_button)
        row.addWidget(self._delete_button)
        row.addStretch(1)
        layout.addLayout(row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._on_selection_changed()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, drafts: list[WeightDraft], *, used_names: set[str]) -> None
```

Build the editor for [`drafts`](#%EF%B8%8F-method-drafts).

Args:

- `parent` (`QWidget | None`): Owner window.
- [`drafts`](#%EF%B8%8F-method-drafts) (`list[WeightDraft]`): Current template weights.
- `used_names` (`set[str]`): Weight names that appear in any set.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        drafts: list[WeightDraft],
        *,
        used_names: set[str],
    ) -> None:
        super().__init__(parent)
        self._used_names = {name.casefold() for name in used_names}
        self.setWindowTitle("Edit dumbbell weights")
        qt_modality.set_owner_window_modal(self)
        self.resize(420, 460)
        self._setup_ui()
        for draft in drafts:
            self._add_item(draft)
```

</details>

### ⚙️ Method `drafts`

```python
def drafts(self) -> list[WeightDraft]
```

Return the edited weight rows.

<details>
<summary>Code:</summary>

```python
def drafts(self) -> list[WeightDraft]:
        result: list[WeightDraft] = []
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is None:
                continue
            original = item.data(_ORIGINAL_NAME_ROLE)
            result.append(
                WeightDraft(
                    original_name=str(original) if original else None,
                    name=item.text().strip(),
                    calories_modifier=float(item.data(_CALORIES_ROLE) or 1.0),
                    name_local=str(item.data(_NAME_LOCAL_ROLE) or ""),
                )
            )
        return result
```

</details>
