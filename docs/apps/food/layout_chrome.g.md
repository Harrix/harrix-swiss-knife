---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `layout_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `install_food_layout_chrome`](#-function-install_food_layout_chrome)
- [🔧 Function `persist_food_stats_splitter_sizes`](#-function-persist_food_stats_splitter_sizes)

</details>

## 🔧 Function `install_food_layout_chrome`

```python
def install_food_layout_chrome(host: Any) -> None
```

Apply soft panes plus Stats-tab Fluent polish.

<details>
<summary>Code:</summary>

```python
def install_food_layout_chrome(host: Any) -> None:
    soft = [
        (host.frame_food_controls, "foodEntryForm"),
        (host.widget_food_middle, "foodEntryItems"),
    ]
    content = [(host.widget_food_log, "foodLogPane")]
    if hasattr(host, "frame") and host.frame is not None:
        soft.append((host.frame, "foodStatsTablePane"))
    if hasattr(host, "widget_food_stats_chart"):
        content.append((host.widget_food_stats_chart, "foodStatsChartPane"))

    boxes = [
        host.groupBox_food_add,
        host.groupBox_food_commands,
        host.groupBox_food_today,
        host.groupBox_food_yesterday,
    ]
    install_tracker_column_chrome(
        host,
        soft_panes=soft,
        content_panes=content,
        quiet_boxes=boxes,
        theme_flag="_food_layout_chrome_theme_bound",
    )
    _polish_stats_tab(host)
    _configure_stats_splitter(host)
    if not getattr(host, "_food_stats_theme_bound", False):
        bind_theme(host, lambda: _polish_stats_tab(host))
        host._food_stats_theme_bound = True  # noqa: SLF001
```

</details>

## 🔧 Function `persist_food_stats_splitter_sizes`

```python
def persist_food_stats_splitter_sizes(host: Any) -> None
```

Save Food Statistics splitter sizes.

<details>
<summary>Code:</summary>

```python
def persist_food_stats_splitter_sizes(host: Any) -> None:
    if getattr(host, "_is_closing", False) or not hasattr(host, "splitter_food_stats"):
        return
    sizes = host.splitter_food_stats.sizes()
    if len(sizes) == _TWO_PANE and all(size > 0 for size in sizes):
        save_splitter_sizes(_STATS_SPLITTER_KEY, [int(size) for size in sizes], _STATS_SPLITTER_DEFAULT)
```

</details>
