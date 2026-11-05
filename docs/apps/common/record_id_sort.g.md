---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `record_id_sort.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RecordIdSortProxyModel`](#%EF%B8%8F-class-recordidsortproxymodel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `lessThan`](#%EF%B8%8F-method-lessthan)
  - [⚙️ Method `sort`](#%EF%B8%8F-method-sort)

</details>

## 🏛️ Class `RecordIdSortProxyModel`

```python
class RecordIdSortProxyModel(QSortFilterProxyModel)
```

Proxy that can sort rows by the database ID stored in the vertical header.

<details>
<summary>Code:</summary>

```python
class RecordIdSortProxyModel(QSortFilterProxyModel):

    def __init__(self, parent: QObject | None = None) -> None:
        """Create a proxy that sorts by a column or by the vertical-header record ID."""
        super().__init__(parent)
        self._sort_by_record_id = False

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Compare record ids when that sort is active; otherwise use the column value."""
        if self._sort_by_record_id:
            return _row_id_less_than(source_left, source_right)
        return super().lessThan(source_left, source_right)

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """Sort by record ID when `column` is the ID sentinel, otherwise by that column."""
        self._sort_by_record_id = column == ROW_ID_SORT_SECTION
        if self._sort_by_record_id:
            super().sort(0, order)
            return
        super().sort(column, order)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Create a proxy that sorts by a column or by the vertical-header record ID.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._sort_by_record_id = False
```

</details>

### ⚙️ Method `lessThan`

```python
def lessThan(self, source_left: QModelIndex | QPersistentModelIndex, source_right: QModelIndex | QPersistentModelIndex) -> bool
```

Compare record ids when that sort is active; otherwise use the column value.

<details>
<summary>Code:</summary>

```python
def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if self._sort_by_record_id:
            return _row_id_less_than(source_left, source_right)
        return super().lessThan(source_left, source_right)
```

</details>

### ⚙️ Method `sort`

```python
def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None
```

Sort by record ID when `column` is the ID sentinel, otherwise by that column.

<details>
<summary>Code:</summary>

```python
def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        self._sort_by_record_id = column == ROW_ID_SORT_SECTION
        if self._sort_by_record_id:
            super().sort(0, order)
            return
        super().sort(column, order)
```

</details>
