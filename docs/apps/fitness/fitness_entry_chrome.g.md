---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fitness_entry_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `exercise_state_text`](#-function-exercise_state_text)
- [🔧 Function `install_fitness_entry_chrome`](#-function-install_fitness_entry_chrome)
- [🔧 Function `persist_sets_splitter_sizes`](#-function-persist_sets_splitter_sizes)
- [🔧 Function `refresh_exercise_state_label`](#-function-refresh_exercise_state_label)

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
