---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `layout_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `install_habits_layout_chrome`](#-function-install_habits_layout_chrome)
- [🔧 Function `persist_habits_tabs_splitter_sizes`](#-function-persist_habits_tabs_splitter_sizes)

</details>

## 🔧 Function `install_habits_layout_chrome`

```python
def install_habits_layout_chrome(host: Any) -> None
```

Polish Habits process column and Charts filters.

<details>
<summary>Code:</summary>

```python
def install_habits_layout_chrome(host: Any) -> None:
    _polish_all(host)
    _configure_habits_splitter(host)
    _configure_charts_splitter(host)
    if not getattr(host, "_habits_tabs_theme_bound", False):
        bind_theme(host, lambda: _polish_all(host))
        host._habits_tabs_theme_bound = True  # noqa: SLF001
```

</details>

## 🔧 Function `persist_habits_tabs_splitter_sizes`

```python
def persist_habits_tabs_splitter_sizes(host: Any) -> None
```

Save Habits and Charts splitter sizes.

<details>
<summary>Code:</summary>

```python
def persist_habits_tabs_splitter_sizes(host: Any) -> None:
    if getattr(host, "_is_closing", False):
        return
    for attr, key, default in (
        ("splitter_habits", _HABITS_SPLITTER_KEY, _HABITS_SPLITTER_DEFAULT),
        ("splitter_charts", _CHARTS_SPLITTER_KEY, _CHARTS_SPLITTER_DEFAULT),
    ):
        splitter = getattr(host, attr, None)
        if splitter is None:
            continue
        sizes = splitter.sizes()
        if len(sizes) == _TWO_PANE and all(size > 0 for size in sizes):
            save_splitter_sizes(key, [int(size) for size in sizes], default)
```

</details>
