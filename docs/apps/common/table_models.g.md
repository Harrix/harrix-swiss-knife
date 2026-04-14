---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `table_models.py`

## 🔧 Function `create_table_proxy_model`

```python
def create_table_proxy_model(data: list[list[object]], headers: list[str]) -> QSortFilterProxyModel
```

Create a proxy model with row IDs stored in the vertical header.

The `id_column` is excluded from displayed columns and is stored as vertical header text.

<details>
<summary>Code:</summary>

```python
def create_table_proxy_model(
    data: list[list[object]],
    headers: list[str],
    *,
    id_column: int = 0,
) -> QSortFilterProxyModel:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(headers)

    for row_idx, row in enumerate(data):
        items = [
            QStandardItem("" if value is None else str(value))
            for col_idx, value in enumerate(row)
            if col_idx != id_column
        ]
        model.appendRow(items)
        model.setVerticalHeaderItem(row_idx, QStandardItem(str(row[id_column])))

    proxy = QSortFilterProxyModel()
    proxy.setSourceModel(model)
    return proxy
```

</details>
