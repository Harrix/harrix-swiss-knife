"""Soft column chrome for Habit Tracker, matching Finance Transactions declutter."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.apps.common.tracker_layout_chrome import install_tracker_column_chrome


def install_habits_layout_chrome(host: Any) -> None:
    """Apply soft left panels and quiet GroupBoxes on Habit tabs."""
    soft: list[tuple[Any, str]] = []
    content: list[tuple[Any, str]] = []
    boxes: list[Any] = []

    if hasattr(host, "frame_habits"):
        soft.append((host.frame_habits, "habitsEntryForm"))
    if hasattr(host, "layoutWidget"):
        soft.append((host.layoutWidget, "habitsChartsForm"))
    if hasattr(host, "widget_charts_heatmap"):
        content.append((host.widget_charts_heatmap, "habitsChartsPane"))

    for name in ("groupBox_habits_5", "groupBox_habits_2"):
        box = getattr(host, name, None)
        if box is not None:
            boxes.append(box)

    if not soft and not boxes:
        return
    install_tracker_column_chrome(
        host,
        soft_panes=soft,
        content_panes=content,
        quiet_boxes=boxes,
        theme_flag="_habits_layout_chrome_theme_bound",
    )
