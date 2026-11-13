---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fitness_entry_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_process_column_visibility`](#-function-apply_process_column_visibility)
- [🔧 Function `apply_process_table_column_widths`](#-function-apply_process_table_column_widths)
- [🔧 Function `exercise_state_text`](#-function-exercise_state_text)
- [🔧 Function `install_fitness_entry_chrome`](#-function-install_fitness_entry_chrome)
- [🔧 Function `persist_sets_splitter_sizes`](#-function-persist_sets_splitter_sizes)
- [🔧 Function `refresh_exercise_state_label`](#-function-refresh_exercise_state_label)
- [🔧 Function `set_process_empty_visible`](#-function-set_process_empty_visible)

</details>

## 🔧 Function `apply_process_column_visibility`

```python
def apply_process_column_visibility(host: Any) -> None
```

Re-apply persisted column visibility after the process table model is ready.

<details>
<summary>Code:</summary>

```python
def apply_process_column_visibility(host: Any) -> None:
    table = host.tableView_process
    flags = load_column_visibility()
    for key, column, _label in TOGGLEABLE_COLUMNS:
        visible = flags.get(key, True)
        if column < 0:
            _set_record_id_visible(table, visible=visible, persist=False)
        else:
            _set_data_column_visible(table, column, visible=visible, persist=False, refill=False)
    _apply_day_header_column_policy(table)
    from harrix_swiss_knife.apps.fitness.process_day_headers import (  # noqa: PLC0415
        ProcessDayHeaderProxy,
        apply_process_day_header_spans,
    )

    if isinstance(table.model(), ProcessDayHeaderProxy):
        apply_process_day_header_spans(table)
    else:
        table.clearSpans()
    apply_process_table_column_widths(table, force=True)
```

</details>

## 🔧 Function `apply_process_table_column_widths`

```python
def apply_process_table_column_widths(table_view: QTableView, *, force: bool = False) -> None
```

Fill the viewport among visible process columns, then keep them Interactive.

<details>
<summary>Code:</summary>

```python
def apply_process_table_column_widths(table_view: QTableView, *, force: bool = False) -> None:
    bind_column_fill_on_resize(table_view, apply_process_table_column_widths)
    if not table_view.isVisible() or user_resized_columns(table_view):
        return
    header = table_view.horizontalHeader()
    count = header.count()
    if count <= 0 or table_view.property("hskColumnFillGuard"):
        return
    viewport_w = table_view.viewport().width()
    if viewport_w <= 0:
        return
    if not force and columns_fill_viewport(table_view):
        return

    visible = [i for i in range(count) if not table_view.isColumnHidden(i)]
    if not visible:
        return

    header.setStretchLastSection(False)
    header.setMinimumSectionSize(min(header.minimumSectionSize(), 24))
    min_size = header.minimumSectionSize()
    widths = _visible_process_column_widths(
        viewport_w,
        count,
        visible=visible,
        min_size=min_size,
    )

    table_view.setProperty("hskColumnFillGuard", 1)
    try:
        for column in range(count):
            header.setSectionResizeMode(column, header.ResizeMode.Interactive)
            table_view.setColumnWidth(column, widths[column] if column in set(visible) else 0)
    finally:
        table_view.setProperty("hskColumnFillGuard", 0)
```

</details>

## 🔧 Function `exercise_state_text`

```python
def exercise_state_text(display_name: str | None) -> str
```

Return the form exercise indicator text (with optional hint when empty).

<details>
<summary>Code:</summary>

```python
def exercise_state_text(display_name: str | None) -> str:
    name = (display_name or "").strip()
    if not name:
        return f"{_NO_EXERCISE}\n{_EXERCISE_HINT}"
    lowered = name.casefold()
    if lowered.startswith(_EXERCISE_PREFIX.casefold()):
        return name
    if lowered in {_NO_EXERCISE.casefold(), "no exercise selected"}:
        return f"{_NO_EXERCISE}\n{_EXERCISE_HINT}"
    return f"{_EXERCISE_PREFIX}{name}"
```

</details>

## 🔧 Function `install_fitness_entry_chrome`

```python
def install_fitness_entry_chrome(host: Any) -> None
```

Polish the Sets form, exercise list, splitter, and process table chrome.

<details>
<summary>Code:</summary>

```python
def install_fitness_entry_chrome(host: Any) -> None:
    _ensure_exercise_list_header(host)
    _ensure_process_empty_label(host)
    _polish_form_column(host)
    _polish_exercise_list(host)
    _polish_exercise_state_label(host)
    _polish_process_table(host)
    _configure_sets_splitter(host)
    if not getattr(host, "_fitness_entry_theme_bound", False):

        def _refresh_theme() -> None:
            _polish_form_column(host)
            _polish_exercise_list(host)
            _polish_exercise_state_label(host)

        bind_theme(host, _refresh_theme)
        host._fitness_entry_theme_bound = True  # noqa: SLF001
```

</details>

## 🔧 Function `persist_sets_splitter_sizes`

```python
def persist_sets_splitter_sizes(host: Any) -> None
```

Save current Sets-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def persist_sets_splitter_sizes(host: Any) -> None:
    if getattr(host, "_is_closing", False) or not hasattr(host, "splitter"):
        return
    sizes = host.splitter.sizes()
    if len(sizes) == EXPECTED_SETS_SPLITTER_LEN and all(size > 0 for size in sizes):
        save_sets_splitter_sizes([int(size) for size in sizes])
```

</details>

## 🔧 Function `refresh_exercise_state_label`

```python
def refresh_exercise_state_label(host: Any, display_name: str | None = None) -> None
```

Update `label_exercise` with a Fluent status string.

<details>
<summary>Code:</summary>

```python
def refresh_exercise_state_label(host: Any, display_name: str | None = None) -> None:
    text = exercise_state_text(display_name)
    selected = bool((display_name or "").strip()) and not text.startswith(_NO_EXERCISE)
    host.label_exercise.setText(text)
    host.label_exercise.setWordWrap(True)
    host.label_exercise.setToolTip(_EXERCISE_HINT if not selected else text.split("\n", 1)[0])
    host.label_exercise.setProperty("hskExerciseSelected", selected)
    host.label_exercise.style().unpolish(host.label_exercise)
    host.label_exercise.style().polish(host.label_exercise)
```

</details>

## 🔧 Function `set_process_empty_visible`

```python
def set_process_empty_visible(host: Any, *, visible: bool) -> None
```

Show or hide the process-history empty state.

<details>
<summary>Code:</summary>

```python
def set_process_empty_visible(host: Any, *, visible: bool) -> None:
    label = getattr(host, "label_process_empty", None)
    if isinstance(label, QLabel):
        label.setVisible(visible)
    table = getattr(host, "tableView_process", None)
    if table is not None:
        table.setVisible(not visible)
```

</details>
