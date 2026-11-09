---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `layout_chrome.py`

## 🔧 Function `install_fitness_layout_chrome`

```python
def install_fitness_layout_chrome(host: Any) -> None
```

Apply soft form/list panes and quiet GroupBoxes on Fitness tabs.

<details>
<summary>Code:</summary>

```python
def install_fitness_layout_chrome(host: Any) -> None:
    soft = [
        (host.frame, "fitnessEntryForm"),
        (host.widget_middle, "fitnessExerciseList"),
    ]
    content = [(host.widget_process, "fitnessProcessPane")]
    boxes = [host.groupBox, host.groupBox_9]

    if hasattr(host, "widget_left_panel"):
        soft.append((host.widget_left_panel, "fitnessChartsForm"))
    if hasattr(host, "widget_right_panel"):
        content.append((host.widget_right_panel, "fitnessChartsPane"))
    if hasattr(host, "groupBox_type_of_charts"):
        boxes.append(host.groupBox_type_of_charts)
    if hasattr(host, "frame_4"):
        soft.append((host.frame_4, "fitnessWeightForm"))
    for name in ("groupBox_4", "groupBox_6", "groupBox_10"):
        box = getattr(host, name, None)
        if box is not None:
            boxes.append(box)

    install_tracker_column_chrome(
        host,
        soft_panes=soft,
        content_panes=content,
        quiet_boxes=boxes,
        theme_flag="_fitness_layout_chrome_theme_bound",
    )
```

</details>
