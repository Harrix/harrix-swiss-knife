---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `table_context_menu.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_date_in_main_field_actions`](#-function-add_date_in_main_field_actions)
- [🔧 Function `add_delete_action`](#-function-add_delete_action)
- [🔧 Function `add_info_action`](#-function-add_info_action)
- [🔧 Function `add_separator`](#-function-add_separator)
- [🔧 Function `last_action_is_separator`](#-function-last_action_is_separator)
- [🔧 Function `show_records_label`](#-function-show_records_label)

</details>

## 🔧 Function `add_date_in_main_field_actions`

```python
def add_date_in_main_field_actions(menu: QMenu) -> tuple[QAction, QAction, QAction]
```

Add the three “set this date in the main field” commands.

<details>
<summary>Code:</summary>

```python
def add_date_in_main_field_actions(menu: QMenu) -> tuple[QAction, QAction, QAction]:
    add_separator(menu)
    set_date = menu.addAction(LABEL_SET_DATE)
    plus_one = menu.addAction(LABEL_SET_DATE_PLUS_ONE)
    minus_one = menu.addAction(LABEL_SET_DATE_MINUS_ONE)
    return set_date, plus_one, minus_one
```

</details>

## 🔧 Function `add_delete_action`

```python
def add_delete_action(menu: QMenu) -> QAction
```

Add `Delete` as the last command, after a separator when needed.

<details>
<summary>Code:</summary>

```python
def add_delete_action(menu: QMenu) -> QAction:
    add_separator(menu)
    return menu.addAction(LABEL_DELETE)
```

</details>

## 🔧 Function `add_info_action`

```python
def add_info_action(menu: QMenu, text: str) -> QAction
```

Add a disabled informational row (sum, totals) before Delete.

<details>
<summary>Code:</summary>

```python
def add_info_action(menu: QMenu, text: str) -> QAction:
    add_separator(menu)
    action = menu.addAction(text)
    action.setEnabled(False)
    return action
```

</details>

## 🔧 Function `add_separator`

```python
def add_separator(menu: QMenu) -> None
```

Add a separator unless the menu is empty or already ends with one.

<details>
<summary>Code:</summary>

```python
def add_separator(menu: QMenu) -> None:
    if menu.isEmpty() or last_action_is_separator(menu):
        return
    menu.addSeparator()
```

</details>

## 🔧 Function `last_action_is_separator`

```python
def last_action_is_separator(menu: QMenu) -> bool
```

Return whether the last menu item is already a separator.

<details>
<summary>Code:</summary>

```python
def last_action_is_separator(menu: QMenu) -> bool:
    actions = menu.actions()
    return bool(actions) and actions[-1].isSeparator()
```

</details>

## 🔧 Function `show_records_label`

```python
def show_records_label(*, show_all: bool, last_count: int) -> str
```

Label that toggles between all records and the last `last_count`.

<details>
<summary>Code:</summary>

```python
def show_records_label(*, show_all: bool, last_count: int) -> str:
    if show_all:
        return f"📋 Show last {last_count}"
    return LABEL_SHOW_ALL_RECORDS
```

</details>
