"""Tests for shared tracker status-bar text formatters."""

from harrix_swiss_knife.apps.common.status_bar_text import (
    format_list_view_status,
    format_selection_count_status,
    format_translate_progress_status,
    is_owned_status_message,
    join_status_parts,
)


def test_format_list_view_status_combines_filter_and_pagination() -> None:
    assert format_list_view_status(filtered=True, loaded_count=45, has_more=True) == (
        "Filtered · 45 loaded · more below"
    )
    assert format_list_view_status() == ""


def test_format_selection_count_status() -> None:
    assert format_selection_count_status(0) == ""
    assert format_selection_count_status(1, detail="sum 12.00 $") == "1 row selected · sum 12.00 $"
    assert format_selection_count_status(2) == "2 rows selected"


def test_format_translate_progress_status_and_ownership() -> None:
    base = "Translating food names…"
    message = format_translate_progress_status(base, 12, item_label="names left")
    assert message == "Translating food names… (12 names left)"
    assert is_owned_status_message(message, base)
    assert is_owned_status_message(base, base)
    assert not is_owned_status_message("Ready", base)


def test_join_status_parts_skips_blanks() -> None:
    assert join_status_parts("A", "", "B", "  ") == "A · B"
