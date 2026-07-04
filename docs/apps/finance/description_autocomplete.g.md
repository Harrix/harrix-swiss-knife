---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `description_autocomplete.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DescriptionAutocompleteProxyModel`](#️-class-descriptionautocompleteproxymodel)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `filterAcceptsRow`](#️-method-filteracceptsrow)
  - [⚙️ Method `lessThan`](#️-method-lessthan)
  - [⚙️ Method `set_filter_text`](#️-method-set_filter_text)
- [🔧 Function `dedupe_descriptions_for_autocomplete`](#-function-dedupe_descriptions_for_autocomplete)
- [🔧 Function `_match_tier`](#-function-_match_tier)

</details>

## 🏛️ Class `DescriptionAutocompleteProxyModel`

```python
class DescriptionAutocompleteProxyModel(QSortFilterProxyModel)
```

Proxy model for description autocomplete with exact/starts-with/contains ordering.

<details>
<summary>Code:</summary>

```python
class DescriptionAutocompleteProxyModel(QSortFilterProxyModel):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the proxy model."""
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:  # noqa: N802
        """Determine if a row should be accepted by the filter."""
        if not self.filter_text:
            return True

        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        data = source_model.data(index, Qt.ItemDataRole.DisplayRole)

        if data is None:
            return False

        text = str(data).lower()
        filter_lower = self.filter_text.lower()

        if text.startswith(filter_lower):
            return True

        return filter_lower in text

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Sort by match tier, then preserve source order within each tier."""
        if not self.filter_text:
            return source_left.row() < source_right.row()

        filter_lower = self.filter_text.lower()
        left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

        if left_data is None or right_data is None:
            return False

        left_tier = _match_tier(str(left_data), filter_lower)
        right_tier = _match_tier(str(right_data), filter_lower)

        if left_tier != right_tier:
            return left_tier < right_tier

        return source_left.row() < source_right.row()

    def set_filter_text(self, text: str) -> None:
        """Set the filter text and trigger re-filtering and sorting."""
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the proxy model.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
```

</details>

### ⚙️ Method `filterAcceptsRow`

```python
def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool
```

Determine if a row should be accepted by the filter.

<details>
<summary>Code:</summary>

```python
def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:  # noqa: N802
        if not self.filter_text:
            return True

        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        data = source_model.data(index, Qt.ItemDataRole.DisplayRole)

        if data is None:
            return False

        text = str(data).lower()
        filter_lower = self.filter_text.lower()

        if text.startswith(filter_lower):
            return True

        return filter_lower in text
```

</details>

### ⚙️ Method `lessThan`

```python
def lessThan(self, source_left: QModelIndex | QPersistentModelIndex, source_right: QModelIndex | QPersistentModelIndex) -> bool
```

Sort by match tier, then preserve source order within each tier.

<details>
<summary>Code:</summary>

```python
def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if not self.filter_text:
            return source_left.row() < source_right.row()

        filter_lower = self.filter_text.lower()
        left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

        if left_data is None or right_data is None:
            return False

        left_tier = _match_tier(str(left_data), filter_lower)
        right_tier = _match_tier(str(right_data), filter_lower)

        if left_tier != right_tier:
            return left_tier < right_tier

        return source_left.row() < source_right.row()
```

</details>

### ⚙️ Method `set_filter_text`

```python
def set_filter_text(self, text: str) -> None
```

Set the filter text and trigger re-filtering and sorting.

<details>
<summary>Code:</summary>

```python
def set_filter_text(self, text: str) -> None:
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)
```

</details>

## 🔧 Function `dedupe_descriptions_for_autocomplete`

```python
def dedupe_descriptions_for_autocomplete(descriptions: list[str]) -> list[str]
```

Return unique descriptions preserving first-seen order.

<details>
<summary>Code:</summary>

```python
def dedupe_descriptions_for_autocomplete(descriptions: list[str]) -> list[str]:
    return list(dict.fromkeys(descriptions))
```

</details>

## 🔧 Function `_match_tier`

```python
def _match_tier(text: str, filter_text: str) -> int
```

Return sort tier: 0 exact, 1 starts-with, 2 contains.

<details>
<summary>Code:</summary>

```python
def _match_tier(text: str, filter_text: str) -> int:
    filter_lower = filter_text.lower()
    text_lower = text.lower()
    if text_lower == filter_lower:
        return 0
    if text_lower.startswith(filter_lower):
        return 1
    return 2
```

</details>
