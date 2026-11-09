"""Soft column chrome for Food Tracker, matching Finance Transactions declutter."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.apps.common.tracker_layout_chrome import install_tracker_column_chrome


def install_food_layout_chrome(host: Any) -> None:
    """Apply soft form/list panes and quiet GroupBoxes on Food tabs."""
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
