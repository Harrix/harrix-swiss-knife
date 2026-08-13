"""Tests for deferred Finance UI refresh after transaction add."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.deferred_ui_refresh import DeferredUiRefreshScheduler


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_mark_sets_dirty_and_flush_clears(qapp: QApplication) -> None:  # noqa: ARG001
    calls: list[bool] = []

    def on_flush(*, categories_may_change: bool) -> None:
        calls.append(categories_may_change)

    scheduler = DeferredUiRefreshScheduler(None, on_flush, interval_ms=50_000)
    assert not scheduler.dirty
    scheduler.mark()
    assert scheduler.dirty
    assert not scheduler.categories_may_change
    scheduler.flush()
    assert not scheduler.dirty
    assert calls == [False]


def test_mark_categories_may_change_sticky_until_flush(qapp: QApplication) -> None:  # noqa: ARG001
    calls: list[bool] = []

    def on_flush(*, categories_may_change: bool) -> None:
        calls.append(categories_may_change)

    scheduler = DeferredUiRefreshScheduler(None, on_flush, interval_ms=50_000)
    scheduler.mark(categories_may_change=False)
    scheduler.mark(categories_may_change=True)
    scheduler.mark(categories_may_change=False)
    assert scheduler.categories_may_change
    scheduler.flush()
    assert calls == [True]
    assert not scheduler.categories_may_change


def test_flush_noop_when_not_dirty(qapp: QApplication) -> None:  # noqa: ARG001
    calls: list[bool] = []

    def on_flush(*, categories_may_change: bool) -> None:
        calls.append(categories_may_change)

    scheduler = DeferredUiRefreshScheduler(None, on_flush, interval_ms=50_000)
    scheduler.flush()
    assert calls == []


def test_stop_cancels_pending_without_flush(qapp: QApplication) -> None:  # noqa: ARG001
    calls: list[bool] = []

    def on_flush(*, categories_may_change: bool) -> None:
        calls.append(categories_may_change)

    scheduler = DeferredUiRefreshScheduler(None, on_flush, interval_ms=50_000)
    scheduler.mark(categories_may_change=True)
    scheduler.stop()
    assert not scheduler.dirty
    assert not scheduler.categories_may_change
    assert calls == []


def test_timer_triggers_flush(qapp: QApplication) -> None:
    calls: list[bool] = []

    def on_flush(*, categories_may_change: bool) -> None:
        calls.append(categories_may_change)

    scheduler = DeferredUiRefreshScheduler(None, on_flush, interval_ms=10)
    scheduler.mark(categories_may_change=True)
    assert scheduler.dirty
    deadline_ms = 500
    elapsed = 0
    while scheduler.dirty and elapsed < deadline_ms:
        loop = QEventLoop()
        QTimer.singleShot(20, loop.quit)
        loop.exec()
        qapp.processEvents()
        elapsed += 20
    assert calls == [True]
    assert not scheduler.dirty
