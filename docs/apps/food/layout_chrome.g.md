---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `layout_chrome.py`

## 🔧 Function `install_food_layout_chrome`

```python
def install_food_layout_chrome(host: Any) -> None
```

Apply soft form/list panes and quiet GroupBoxes on Food tabs.

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
```

</details>
