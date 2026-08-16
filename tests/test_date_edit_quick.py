"""Tests for date-edit quick button labels."""

from __future__ import annotations

from PySide6.QtCore import QDate

from harrix_swiss_knife.apps.common.date_edit_quick import date_quick_button_label


def test_date_quick_button_label_today_yesterday_and_other() -> None:
    today = QDate(2026, 8, 16)
    assert date_quick_button_label(today, today=today) == "📅 Today"
    assert date_quick_button_label(today.addDays(-1), today=today) == "📅 Yesterday"
    assert date_quick_button_label(today.addDays(-2), today=today) == "➕ Add + 1"  # noqa: RUF001
    assert date_quick_button_label(today.addDays(1), today=today) == "➕ Add + 1"  # noqa: RUF001
