---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `process_filter_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `advanced_process_filter_count`](#-function-advanced_process_filter_count)
- [🔧 Function `advanced_process_filter_is_active`](#-function-advanced_process_filter_is_active)
- [🔧 Function `install_process_filter_chrome`](#-function-install_process_filter_chrome)
- [🔧 Function `refresh_process_filter_chips`](#-function-refresh_process_filter_chips)
- [🔧 Function `selected_process_filter_value`](#-function-selected_process_filter_value)
- [🔧 Function `sync_process_filter_button`](#-function-sync_process_filter_button)

</details>

## 🔧 Function `advanced_process_filter_count`

```python
def advanced_process_filter_count(host: Any) -> int
```

Return how many process filters are applied (exercise, type, date).

<details>
<summary>Code:</summary>

```python
def advanced_process_filter_count(host: Any) -> int:
    count = 0
    if selected_process_filter_value(host.comboBox_filter_exercise.currentText()):
        count += 1
    if selected_process_filter_value(host.comboBox_filter_type.currentText()):
        count += 1
    if host.checkBox_use_date_filter.isChecked():
        count += 1
    return count
```

</details>

## 🔧 Function `advanced_process_filter_is_active`

```python
def advanced_process_filter_is_active(host: Any) -> bool
```

Return whether any process advanced filter is applied.

<details>
<summary>Code:</summary>

```python
def advanced_process_filter_is_active(host: Any) -> bool:
    return advanced_process_filter_count(host) > 0
```

</details>

## 🔧 Function `install_process_filter_chrome`

```python
def install_process_filter_chrome(host: Any) -> None
```

Rebuild the process filter strip: exercise/type always on, dates behind Filter.

<details>
<summary>Code:</summary>

```python
def install_process_filter_chrome(host: Any) -> None:
    hide_filter_labels(
        host.label_filter_exercise,
        host.label_filter_type,
        host.label_filter_date,
        host.label_filter_to,
    )
    if host.comboBox_filter_exercise.count() == 0:
        host.comboBox_filter_exercise.addItem(FILTER_ALL_EXERCISES)
    elif not host.comboBox_filter_exercise.itemText(0).strip():
        host.comboBox_filter_exercise.setItemText(0, FILTER_ALL_EXERCISES)
    if host.comboBox_filter_type.count() == 0:
        host.comboBox_filter_type.addItem(FILTER_ALL_TYPES)
    elif not host.comboBox_filter_type.itemText(0).strip():
        host.comboBox_filter_type.setItemText(0, FILTER_ALL_TYPES)
    prepare_filter_combo(host.comboBox_filter_exercise, FILTER_ALL_EXERCISES, "Exercise")
    prepare_filter_combo(host.comboBox_filter_type, FILTER_ALL_TYPES, "Type")
    prepare_date_filter_fields(
        host.dateEdit_filter_from,
        host.dateEdit_filter_to,
        host.checkBox_use_date_filter,
    )
    install_tracker_filter_shell(
        host,
        object_name_prefix="process",
        search_edit=None,
        search_placeholder="",
        toolbar_widgets=(host.comboBox_filter_exercise, host.comboBox_filter_type),
        advanced_rows=(
            (
                inline_filter_caption("From", host.dateEdit_filter_from, host.groupBox_filter),
                inline_filter_caption("To", host.dateEdit_filter_to, host.groupBox_filter),
                host.checkBox_use_date_filter,
            ),
        ),
        vertical_layout=host.verticalLayout_process,
        table_widget=host.tableView_process,
    )
```

</details>

## 🔧 Function `refresh_process_filter_chips`

```python
def refresh_process_filter_chips(host: Any) -> None
```

Rebuild closable chips for active process filters.

<details>
<summary>Code:</summary>

```python
def refresh_process_filter_chips(host: Any) -> None:
    chips: list[tuple[str, Any]] = []
    exercise = selected_process_filter_value(host.comboBox_filter_exercise.currentText())
    if exercise:
        chips.append((exercise, host.clear_process_exercise_filter))
    exercise_type = selected_process_filter_value(host.comboBox_filter_type.currentText())
    if exercise_type:
        chips.append((exercise_type, host.clear_process_type_filter))
    if host.checkBox_use_date_filter.isChecked():
        date_from = host.dateEdit_filter_from.date().toString("yyyy-MM-dd")
        date_to = host.dateEdit_filter_to.date().toString("yyyy-MM-dd")
        chips.append((f"{date_from} → {date_to}", host.clear_process_date_filter))
    refresh_tracker_filter_chips(host, chips)
```

</details>

## 🔧 Function `selected_process_filter_value`

```python
def selected_process_filter_value(text: str) -> str
```

Return a concrete process filter value, or `""` for an `all` sentinel.

<details>
<summary>Code:</summary>

```python
def selected_process_filter_value(text: str) -> str:
    value = text.strip()
    return "" if value in _FILTER_ALL_VALUES else value
```

</details>

## 🔧 Function `sync_process_filter_button`

```python
def sync_process_filter_button(host: Any) -> None
```

Update Filter button text with the active filter count.

<details>
<summary>Code:</summary>

```python
def sync_process_filter_button(host: Any) -> None:
    if hasattr(host, "pushButton_filter"):
        count = advanced_process_filter_count(host)
        host.pushButton_filter.setText(f"Filter ({count})" if count else "Filter")
```

</details>
