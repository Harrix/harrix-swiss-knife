---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `categories_table.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CategoriesTableProxyModel`](#%EF%B8%8F-class-categoriestableproxymodel)
  - [⚙️ Method `lessThan`](#%EF%B8%8F-method-lessthan)
- [🔧 Function `create_categories_table_proxy_model`](#-function-create_categories_table_proxy_model)

</details>

## 🏛️ Class `CategoriesTableProxyModel`

```python
class CategoriesTableProxyModel(QSortFilterProxyModel)
```

Sort categories by type, then by plain name (ignoring display icon).

<details>
<summary>Code:</summary>

```python
class CategoriesTableProxyModel(QSortFilterProxyModel):

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Compare rows by type UserRole, then name UserRole."""
        source_model = self.sourceModel()
        if source_model is None:
            return False

        left_type = source_model.data(source_left.sibling(source_left.row(), 1), Qt.ItemDataRole.UserRole)
        right_type = source_model.data(source_right.sibling(source_right.row(), 1), Qt.ItemDataRole.UserRole)
        left_type_value = 0 if left_type is None else int(left_type)
        right_type_value = 0 if right_type is None else int(right_type)
        if left_type_value != right_type_value:
            return left_type_value < right_type_value

        left_name = source_model.data(source_left.sibling(source_left.row(), 0), Qt.ItemDataRole.UserRole) or ""
        right_name = source_model.data(source_right.sibling(source_right.row(), 0), Qt.ItemDataRole.UserRole) or ""
        left_fold = str(left_name).casefold()
        right_fold = str(right_name).casefold()
        if left_fold != right_fold:
            return left_fold < right_fold
        return source_left.row() < source_right.row()
```

</details>

### ⚙️ Method `lessThan`

```python
def lessThan(self, source_left: QModelIndex | QPersistentModelIndex, source_right: QModelIndex | QPersistentModelIndex) -> bool
```

Compare rows by type UserRole, then name UserRole.

<details>
<summary>Code:</summary>

```python
def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        source_model = self.sourceModel()
        if source_model is None:
            return False

        left_type = source_model.data(source_left.sibling(source_left.row(), 1), Qt.ItemDataRole.UserRole)
        right_type = source_model.data(source_right.sibling(source_right.row(), 1), Qt.ItemDataRole.UserRole)
        left_type_value = 0 if left_type is None else int(left_type)
        right_type_value = 0 if right_type is None else int(right_type)
        if left_type_value != right_type_value:
            return left_type_value < right_type_value

        left_name = source_model.data(source_left.sibling(source_left.row(), 0), Qt.ItemDataRole.UserRole) or ""
        right_name = source_model.data(source_right.sibling(source_right.row(), 0), Qt.ItemDataRole.UserRole) or ""
        left_fold = str(left_name).casefold()
        right_fold = str(right_name).casefold()
        if left_fold != right_fold:
            return left_fold < right_fold
        return source_left.row() < source_right.row()
```

</details>

## 🔧 Function `create_categories_table_proxy_model`

```python
def create_categories_table_proxy_model(rows: list[tuple[str, str, int, str, str, object, object]], headers: list[str]) -> CategoriesTableProxyModel
```

Build categories proxy from display rows.

Args:

- `rows` (`list[tuple]`): Each item is
  `(display_name, type_label, type_value, plain_name, name_local, color, row_id)`.
- `headers` (`list[str]`): Column headers for display columns.

Returns:

- [`CategoriesTableProxyModel`](#%EF%B8%8F-class-categoriestableproxymodel): Sorted proxy model.

<details>
<summary>Code:</summary>

```python
def create_categories_table_proxy_model(
    rows: list[tuple[str, str, int, str, str, object, object]],
    headers: list[str],
) -> CategoriesTableProxyModel:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(headers)

    for row_idx, (display_name, type_label, type_value, plain_name, name_local, color, row_id) in enumerate(rows):
        name_item = QStandardItem(display_name)
        name_item.setData(plain_name, Qt.ItemDataRole.UserRole)
        name_item.setBackground(QBrush(color))
        name_item.setEditable(False)

        type_item = QStandardItem(type_label)
        type_item.setData(type_value, Qt.ItemDataRole.UserRole)
        type_item.setBackground(QBrush(color))
        type_item.setEditable(False)

        name_local_item = QStandardItem(name_local)
        name_local_item.setBackground(QBrush(color))
        name_local_item.setEditable(False)

        model.appendRow([name_item, type_item, name_local_item])
        model.setVerticalHeaderItem(row_idx, QStandardItem(str(row_id)))

    proxy = CategoriesTableProxyModel()
    proxy.setSourceModel(model)
    proxy.sort(0)
    return proxy
```

</details>
