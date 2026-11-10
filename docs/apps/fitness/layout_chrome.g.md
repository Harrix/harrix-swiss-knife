---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `layout_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_exercises_splitter_sizes`](#-function-apply_exercises_splitter_sizes)
- [🔧 Function `install_fitness_layout_chrome`](#-function-install_fitness_layout_chrome)
- [🔧 Function `persist_fitness_tabs_splitter_sizes`](#-function-persist_fitness_tabs_splitter_sizes)

</details>

## 🔧 Function `apply_exercises_splitter_sizes`

```python
def apply_exercises_splitter_sizes(host: Any) -> None
```

Re-apply the Exercises 50/50 splitter after the tab is shown.

<details>
<summary>Code:</summary>

```python
def apply_exercises_splitter_sizes(host: Any) -> None:
    apply = getattr(host, "_apply_fitness_exercises_splitter_sizes", None)
    if callable(apply):
        apply()
```

</details>

## 🔧 Function `install_fitness_layout_chrome`

```python
def install_fitness_layout_chrome(host: Any) -> None
```

Polish Charts / Exercises / Weight / Statistics secondary tabs.

<details>
<summary>Code:</summary>

```python
def install_fitness_layout_chrome(host: Any) -> None:
    _polish_all(host)
    _configure_charts_splitter(host)
    _configure_exercises_splitter(host)
    if not getattr(host, "_fitness_tabs_theme_bound", False):
        bind_theme(host, lambda: _polish_all(host))
        host._fitness_tabs_theme_bound = True  # noqa: SLF001
```

</details>

## 🔧 Function `persist_fitness_tabs_splitter_sizes`

```python
def persist_fitness_tabs_splitter_sizes(host: Any) -> None
```

Save Charts and Exercises splitter sizes.

<details>
<summary>Code:</summary>

```python
def persist_fitness_tabs_splitter_sizes(host: Any) -> None:
    if getattr(host, "_is_closing", False):
        return
    for attr, key, default in (
        ("splitter_charts", _CHARTS_SPLITTER_KEY, _CHARTS_SPLITTER_DEFAULT),
        ("splitter_2", _EXERCISES_SPLITTER_KEY, _EXERCISES_SPLITTER_DEFAULT),
    ):
        splitter = getattr(host, attr, None)
        if splitter is None:
            continue
        sizes = splitter.sizes()
        if len(sizes) == _TWO_PANE and all(size > 0 for size in sizes):
            save_splitter_sizes(key, [int(size) for size in sizes], default)
```

</details>
