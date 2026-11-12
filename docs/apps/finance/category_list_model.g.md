---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_list_model.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `fill_category_picker_model`](#-function-fill_category_picker_model)
- [🔧 Function `find_category_in_picker`](#-function-find_category_in_picker)
- [🔧 Function `iter_category_picker_rows`](#-function-iter_category_picker_rows)
- [🔧 Function `selected_category_name`](#-function-selected_category_name)

</details>

## 🔧 Function `fill_category_picker_model`

```python
def fill_category_picker_model(model: QStandardItemModel, *, expense_categories: Sequence[CategoryIconRow], income_categories: Sequence[CategoryIconRow]) -> None
```

Fill one model: Expense section, expense rows, Income section, income rows.

<details>
<summary>Code:</summary>

```python
def fill_category_picker_model(
    model: QStandardItemModel,
    *,
    expense_categories: Sequence[CategoryIconRow],
    income_categories: Sequence[CategoryIconRow],
) -> None:
    model.clear()
    _append_section(model, "Expense")
    for category_name, icon, name_local, icon_lucide in expense_categories:
        _append_category(model, category_name, icon, name_local, icon_lucide)
    _append_section(model, "Income")
    for category_name, icon, name_local, icon_lucide in income_categories:
        _append_category(model, category_name, icon, name_local, icon_lucide)
```

</details>

## 🔧 Function `find_category_in_picker`

```python
def find_category_in_picker(host: Any, category_name: str) -> QModelIndex | None
```

Locate `category_name` in the category picker list.

<details>
<summary>Code:</summary>

```python
def find_category_in_picker(
    host: Any,
    category_name: str,
) -> QModelIndex | None:
    target = category_name.strip()
    if not target:
        return None
    model = host.listView_categories.model()
    if model is None:
        return None
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if bool(index.data(IS_SECTION_ROLE)):
            continue
        value = model.data(index, Qt.ItemDataRole.UserRole)
        if value is not None and str(value) == target:
            return index
    return None
```

</details>

## 🔧 Function `iter_category_picker_rows`

```python
def iter_category_picker_rows(host: Any) -> Iterator[tuple[QModelIndex, str, str]]
```

Yield `(index, name, name_local)` for every real category row.

<details>
<summary>Code:</summary>

```python
def iter_category_picker_rows(host: Any) -> Iterator[tuple[QModelIndex, str, str]]:
    model = host.listView_categories.model()
    if model is None:
        return
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if bool(index.data(IS_SECTION_ROLE)):
            continue
        name = model.data(index, Qt.ItemDataRole.UserRole)
        if not name:
            continue
        local = model.data(index, NAME_LOCAL_ROLE)
        yield index, str(name), "" if local is None else str(local)
```

</details>

## 🔧 Function `selected_category_name`

```python
def selected_category_name(host: Any) -> str | None
```

Return the selected category name, ignoring section headers.

<details>
<summary>Code:</summary>

```python
def selected_category_name(host: Any) -> str | None:
    index = host.listView_categories.currentIndex()
    if not index.isValid() or bool(index.data(IS_SECTION_ROLE)):
        return None
    value = index.data(Qt.ItemDataRole.UserRole)
    if value is None:
        return None
    text = str(value).strip()
    return text or None
```

</details>
