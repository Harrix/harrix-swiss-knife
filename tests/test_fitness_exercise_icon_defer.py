"""Tests for deferred exercise-icon decode queue ordering."""

from __future__ import annotations

from collections import OrderedDict

from harrix_swiss_knife.apps.fitness.main import (
    enqueue_deferred_exercise_icon,
    prioritize_deferred_exercise_icons,
)


def test_enqueue_deferred_exercise_icon_keeps_unique_fifo_order() -> None:
    pending: OrderedDict[str, None] = OrderedDict()
    enqueue_deferred_exercise_icon(pending, "Squats")
    enqueue_deferred_exercise_icon(pending, "Plank")
    enqueue_deferred_exercise_icon(pending, "Squats")
    enqueue_deferred_exercise_icon(pending, "  ")
    assert list(pending) == ["Squats", "Plank"]


def test_prioritize_deferred_exercise_icons_moves_list_prefix_to_front() -> None:
    pending: OrderedDict[str, None] = OrderedDict()
    for name in ("A", "B", "C", "D", "E"):
        enqueue_deferred_exercise_icon(pending, name)
    prioritize_deferred_exercise_icons(pending, ["D", "B", "Z"])
    assert list(pending) == ["D", "B", "A", "C", "E"]
    assert pending.popitem(last=False)[0] == "D"
    assert pending.popitem(last=False)[0] == "B"
