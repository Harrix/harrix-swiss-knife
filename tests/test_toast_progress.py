"""Tests for progress toast notification."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.toast_progress_notification import ToastProgressNotification


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_progress_toast_updates_bar(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Rendering…", total=10)
    assert toast.total == 10
    assert toast.done == 0
    assert toast.progress_bar.maximum() == 10
    assert toast.progress_bar.value() == 0

    toast.set_progress(4)
    assert toast.done == 4
    assert toast.progress_bar.value() == 4

    toast.set_progress(12)
    assert toast.done == 10
    assert toast.progress_bar.value() == 10

    toast.set_progress(3, total=20)
    assert toast.total == 20
    assert toast.done == 3
    assert toast.progress_bar.maximum() == 20
    toast.close()


def test_progress_toast_zero_total_is_indeterminate(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Working…", total=0)
    assert toast.progress_bar.minimum() == 0
    assert toast.progress_bar.maximum() == 0
    toast.set_progress(5)
    assert toast.done == 5
    toast.close()


def test_progress_toast_cancel_emits_once(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Opening folder…", cancellable=True)
    cancelled: list[int] = []
    toast.cancel_requested.connect(lambda: cancelled.append(1))
    toast.close()
    toast.close()
    assert cancelled == [1]


def test_progress_toast_detail_line(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Syncing…", total=4)
    assert toast.detail_label.isHidden()
    toast.set_detail("English: TickTick Done 2026-08-01")
    assert not toast.detail_label.isHidden()
    assert toast.detail_label.text() == "English: TickTick Done 2026-08-01"
    toast.set_detail("")
    assert toast.detail_label.isHidden()
    toast.close()
