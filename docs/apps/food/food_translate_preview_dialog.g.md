---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_translate_preview_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodTranslatePreviewDialog`](#️-class-foodtranslatepreviewdialog)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `get_translations_to_apply`](#️-method-get_translations_to_apply)

</details>

## 🏛️ Class `FoodTranslatePreviewDialog`

```python
class FoodTranslatePreviewDialog(QDialog)
```

Show Russian → English mappings and apply only after user confirmation.

<details>
<summary>Code:</summary>

```python
class FoodTranslatePreviewDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        names: list[str],
        translations: dict[str, str],
        unique_names_limit: int,
        *,
        filled_from_existing: int = 0,
    ) -> None:
        """Initialize the preview dialog.

        Args:

        - `parent` (`QWidget | None`): Parent window.
        - `names` (`list[str]`): Russian names sent to the AI.
        - `translations` (`dict[str, str]`): Parsed AI translations keyed by name.
        - `unique_names_limit` (`int`): Max unique names per BotHub batch from config.
        - `filled_from_existing` (`int`): Names already filled from the database before AI.

        """
        super().__init__(parent)
        self.setWindowTitle("Translate with AI — preview")
        self.resize(720, 480)

        layout = QVBoxLayout(self)

        with_translation = sum(1 for name in names if translations.get(name))
        filled_note = (
            f"Already filled from database before AI: {filled_from_existing}.\n" if filled_from_existing > 0 else ""
        )
        summary = QLabel(
            f"{filled_note}"
            f"Unique names sent to AI: {len(names)} (batch limit {unique_names_limit}). "
            f"AI returned {with_translation} translation(s).",
            self,
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)

        self._table = QTableWidget(self)
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Name (RU)", "English name"])
        self._table.setRowCount(len(names))
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = self._table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        for row_idx, name in enumerate(names):
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row_idx, 0, name_item)

            english = translations.get(name, "")
            english_item = QTableWidgetItem(english)
            self._table.setItem(row_idx, 1, english_item)

        layout.addWidget(self._table)

        button_box = QDialogButtonBox(self)
        apply_button = button_box.addButton("Apply translations", QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        apply_button.setDefault(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_translations_to_apply(self) -> dict[str, str]:
        """Return name → English pairs with non-empty English values from the table.

        Returns:

        - `dict[str, str]`: Translations to write to the database.

        """
        result: dict[str, str] = {}
        for row_idx in range(self._table.rowCount()):
            name_item = self._table.item(row_idx, 0)
            english_item = self._table.item(row_idx, 1)
            if name_item is None or english_item is None:
                continue
            name = name_item.text().strip()
            name_en = english_item.text().strip()
            if name and name_en:
                result[name] = name_en
        return result
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, names: list[str], translations: dict[str, str], unique_names_limit: int) -> None
```

Initialize the preview dialog.

Args:

- `parent` (`QWidget | None`): Parent window.
- `names` (`list[str]`): Russian names sent to the AI.
- `translations` (`dict[str, str]`): Parsed AI translations keyed by name.
- `unique_names_limit` (`int`): Max unique names per BotHub batch from config.
- `filled_from_existing` (`int`): Names already filled from the database before AI.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        names: list[str],
        translations: dict[str, str],
        unique_names_limit: int,
        *,
        filled_from_existing: int = 0,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Translate with AI — preview")
        self.resize(720, 480)

        layout = QVBoxLayout(self)

        with_translation = sum(1 for name in names if translations.get(name))
        filled_note = (
            f"Already filled from database before AI: {filled_from_existing}.\n" if filled_from_existing > 0 else ""
        )
        summary = QLabel(
            f"{filled_note}"
            f"Unique names sent to AI: {len(names)} (batch limit {unique_names_limit}). "
            f"AI returned {with_translation} translation(s).",
            self,
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)

        self._table = QTableWidget(self)
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Name (RU)", "English name"])
        self._table.setRowCount(len(names))
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = self._table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        for row_idx, name in enumerate(names):
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row_idx, 0, name_item)

            english = translations.get(name, "")
            english_item = QTableWidgetItem(english)
            self._table.setItem(row_idx, 1, english_item)

        layout.addWidget(self._table)

        button_box = QDialogButtonBox(self)
        apply_button = button_box.addButton("Apply translations", QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        apply_button.setDefault(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
```

</details>

### ⚙️ Method `get_translations_to_apply`

```python
def get_translations_to_apply(self) -> dict[str, str]
```

Return name → English pairs with non-empty English values from the table.

Returns:

- `dict[str, str]`: Translations to write to the database.

<details>
<summary>Code:</summary>

```python
def get_translations_to_apply(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for row_idx in range(self._table.rowCount()):
            name_item = self._table.item(row_idx, 0)
            english_item = self._table.item(row_idx, 1)
            if name_item is None or english_item is None:
                continue
            name = name_item.text().strip()
            name_en = english_item.text().strip()
            if name and name_en:
                result[name] = name_en
        return result
```

</details>
