"""Soft column chrome for Finance tabs beyond Transactions entry."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.apps.common.tracker_layout_chrome import install_tracker_column_chrome


def install_finance_layout_chrome(host: Any) -> None:
    """Apply soft left panels on Accounts / Exchange / Rates / Charts / Reports."""
    soft: list[tuple[Any, str]] = []
    boxes: list[Any] = []

    for widget, name in (
        (getattr(host, "frame_accounts", None), "financeAccountsForm"),
        (getattr(host, "frame_exchange", None), "financeExchangeForm"),
        (getattr(host, "frame_rates", None), "financeRatesForm"),
        (getattr(host, "frame_accounts_2", None), "financeChartsForm"),
        (getattr(host, "frame_5", None), "financeReportsForm"),
    ):
        if widget is not None:
            soft.append((widget, name))

    for name in (
        "groupBox_balance_accounts",
        "groupBox_exchange_operation",
        "groupBox_rate_commands",
        "groupBox_filter_2",
        "groupBox_type_of_charts",
        "groupBox_10",
        "groupBox_summary",
    ):
        box = getattr(host, name, None)
        if box is not None:
            boxes.append(box)

    if not soft and not boxes:
        return
    install_tracker_column_chrome(
        host,
        soft_panes=soft,
        quiet_boxes=boxes,
        theme_flag="_finance_layout_chrome_theme_bound",
    )
