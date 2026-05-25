---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_translate_preview_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodTranslatePreviewDialog`](#%EF%B8%8F-class-foodtranslatepreviewdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_translations_to_apply`](#%EF%B8%8F-method-get_translations_to_apply)

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
        *,
        record_limit: int,
    ) -> None:
        """Initialize the preview dialog.

        Args:

        - `parent` (`QWidget | None`): Parent window.
        - `names` (`list[str]`): Russian names sent to the AI.
        - `translations` (`dict[str, str]`): Parsed AI translations keyed by name.
        - `record_limit` (`int`): Max food_log rows considered (lowest `_id`).

        """
        super().__init__(parent)
        self.setWindowTitle("Translate with AI — preview")
        self.resize(720, 480)

        layout = QVBoxLayout(self)

        with_translation = sum(1 for name in names if translations.get(name))
        summary = QLabel(
            f"Unique names: {len(names)}. "
            f"AI returned {with_translation} translation(s). "
            f"Scope: up to {record_limit} food_log row(s) with the smallest _id and empty English name.",
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
def __init__(self, parent: QWidget | None, names: list[str], translations: dict[str, str]) -> None
```

Initialize the preview dialog.

Args:

- `parent` (`QWidget | None`): Parent window.
- `names` (`list[str]`): Russian names sent to the AI.
- `translations` (`dict[str, str]`): Parsed AI translations keyed by name.
- `record_limit` (`int`): Max food_log rows considered (lowest `_id`).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        names: list[str],
        translations: dict[str, str],
        *,
        record_limit: int,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Translate with AI — preview")
        self.resize(720, 480)

        layout = QVBoxLayout(self)

        with_translation = sum(1 for name in names if translations.get(name))
        summary = QLabel(
            f"Unique names: {len(names)}. "
            f"AI returned {with_translation} translation(s). "
            f"Scope: up to {record_limit} food_log row(s) with the smallest _id and empty English name.",
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
