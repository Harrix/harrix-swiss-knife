---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_name_autocomplete.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodNameAutocompleteProxyModel`](#️-class-foodnameautocompleteproxymodel)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `filterAcceptsRow`](#️-method-filteracceptsrow)
  - [⚙️ Method `lessThan`](#️-method-lessthan)
  - [⚙️ Method `set_filter_text`](#️-method-set_filter_text)

</details>

## 🏛️ Class `FoodNameAutocompleteProxyModel`

```python
class FoodNameAutocompleteProxyModel(QSortFilterProxyModel)
```

Proxy model for food name autocomplete with exact/starts-with/contains ordering.

<details>
<summary>Code:</summary>

```python
class FoodNameAutocompleteProxyModel(QSortFilterProxyModel):

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
        """Sort by match tier, then alphabetically (case-insensitive) within tier."""
        if not self.filter_text:
            left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
            right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)
            if left_data is None or right_data is None:
                return False
            left_lower = str(left_data).lower()
            right_lower = str(right_data).lower()
            if left_lower != right_lower:
                return left_lower < right_lower
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

        left_lower = str(left_data).lower()
        right_lower = str(right_data).lower()
        if left_lower != right_lower:
            return left_lower < right_lower

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

Sort by match tier, then alphabetically (case-insensitive) within tier.

<details>
<summary>Code:</summary>

```python
def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if not self.filter_text:
            left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
            right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)
            if left_data is None or right_data is None:
                return False
            left_lower = str(left_data).lower()
            right_lower = str(right_data).lower()
            if left_lower != right_lower:
                return left_lower < right_lower
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

        left_lower = str(left_data).lower()
        right_lower = str(right_data).lower()
        if left_lower != right_lower:
            return left_lower < right_lower

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
