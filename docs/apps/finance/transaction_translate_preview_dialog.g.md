---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transaction_translate_preview_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TransactionTranslatePreviewDialog`](#%EF%B8%8F-class-transactiontranslatepreviewdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `accept`](#%EF%B8%8F-method-accept)
  - [⚙️ Method `get_translations_to_apply`](#%EF%B8%8F-method-get_translations_to_apply)

</details>

## 🏛️ Class `TransactionTranslatePreviewDialog`

```python
class TransactionTranslatePreviewDialog(QDialog)
```

Show description translations before applying them.

<details>
<summary>Code:</summary>

```python
class TransactionTranslatePreviewDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        descriptions: list[str],
        translations: dict[str, str],
        unique_descriptions_limit: int,
        *,
        filled_from_existing: int = 0,
    ) -> None:
        """Initialize transaction translation preview."""
        super().__init__(parent)
        self.setWindowTitle("Translate with AI — preview")
        self.resize(720, 480)
        self._accepted_translations: dict[str, str] | None = None

        layout = QVBoxLayout(self)
        translated = sum(1 for description in descriptions if translations.get(description))
        filled_note = (
            f"Already filled from database before AI: {filled_from_existing}.\n" if filled_from_existing else ""
        )
        summary = QLabel(
            f"{filled_note}Unique descriptions sent to AI: {len(descriptions)} "
            f"(batch limit {unique_descriptions_limit}). AI returned {translated} translation(s).",
            self,
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)

        self._table = QTableWidget(self)
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Description", "English"])
        self._table.setRowCount(len(descriptions))
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = self._table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        for row_idx, description in enumerate(descriptions):
            description_item = QTableWidgetItem(description)
            description_item.setFlags(description_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row_idx, 0, description_item)
            self._table.setItem(row_idx, 1, QTableWidgetItem(translations.get(description, "")))
        layout.addWidget(self._table)

        button_box = QDialogButtonBox(self)
        apply_button = button_box.addButton("Apply translations", QDialogButtonBox.ButtonRole.AcceptRole)
        apply_button.setIcon(create_emoji_icon(OK_BUTTON_EMOJI))
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(button_box)
        apply_button.setDefault(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self) -> None:
        """Commit in-progress cell edits, then close with Accepted."""
        commit_table_editor_if_open(self._table)
        self._accepted_translations = self._read_translations_from_table()
        super().accept()

    def get_translations_to_apply(self) -> dict[str, str]:
        """Return non-empty description-to-English pairs."""
        if self._accepted_translations is not None:
            return self._accepted_translations
        commit_table_editor_if_open(self._table)
        return self._read_translations_from_table()

    def _read_translations_from_table(self) -> dict[str, str]:
        """Read current table cells into a description → English map."""
        result: dict[str, str] = {}
        for row_idx in range(self._table.rowCount()):
            description_item = self._table.item(row_idx, 0)
            english_item = self._table.item(row_idx, 1)
            if description_item is None or english_item is None:
                continue
            description = description_item.text().strip()
            description_en = english_item.text().strip()
            if description and description_en:
                result[description] = description_en
        return result
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, descriptions: list[str], translations: dict[str, str], unique_descriptions_limit: int) -> None
```

Initialize transaction translation preview.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        descriptions: list[str],
        translations: dict[str, str],
        unique_descriptions_limit: int,
        *,
        filled_from_existing: int = 0,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Translate with AI — preview")
        self.resize(720, 480)
        self._accepted_translations: dict[str, str] | None = None

        layout = QVBoxLayout(self)
        translated = sum(1 for description in descriptions if translations.get(description))
        filled_note = (
            f"Already filled from database before AI: {filled_from_existing}.\n" if filled_from_existing else ""
        )
        summary = QLabel(
            f"{filled_note}Unique descriptions sent to AI: {len(descriptions)} "
            f"(batch limit {unique_descriptions_limit}). AI returned {translated} translation(s).",
            self,
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)

        self._table = QTableWidget(self)
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Description", "English"])
        self._table.setRowCount(len(descriptions))
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = self._table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        for row_idx, description in enumerate(descriptions):
            description_item = QTableWidgetItem(description)
            description_item.setFlags(description_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row_idx, 0, description_item)
            self._table.setItem(row_idx, 1, QTableWidgetItem(translations.get(description, "")))
        layout.addWidget(self._table)

        button_box = QDialogButtonBox(self)
        apply_button = button_box.addButton("Apply translations", QDialogButtonBox.ButtonRole.AcceptRole)
        apply_button.setIcon(create_emoji_icon(OK_BUTTON_EMOJI))
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(button_box)
        apply_button.setDefault(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
```

</details>

### ⚙️ Method `accept`

```python
def accept(self) -> None
```

Commit in-progress cell edits, then close with Accepted.

<details>
<summary>Code:</summary>

```python
def accept(self) -> None:
        commit_table_editor_if_open(self._table)
        self._accepted_translations = self._read_translations_from_table()
        super().accept()
```

</details>

### ⚙️ Method `get_translations_to_apply`

```python
def get_translations_to_apply(self) -> dict[str, str]
```

Return non-empty description-to-English pairs.

<details>
<summary>Code:</summary>

```python
def get_translations_to_apply(self) -> dict[str, str]:
        if self._accepted_translations is not None:
            return self._accepted_translations
        commit_table_editor_if_open(self._table)
        return self._read_translations_from_table()
```

</details>
