"""Detached Finance QThreads must be joinable before process quit."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance import exchange_rates_operations as ops


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


class _ShortWorker(QThread):
    def run(self) -> None:
        self.msleep(50)


def test_join_released_qthreads_waits_for_detached_worker(qapp: QApplication) -> None:  # noqa: ARG001
    worker = _ShortWorker()
    worker.start()
    ops.stop_running_qthread(worker)
    assert worker in ops._released_qthreads  # noqa: SLF001
    ops.join_released_qthreads(timeout_ms=2000)
    assert not worker.isRunning()
    assert worker not in ops._released_qthreads  # noqa: SLF001


def test_unparented_qthread_survives_fluent_theme_refresh(qapp: QApplication) -> None:
    """Window-owned QThreads die on Fluent refresh; unparented workers must not."""
    from PySide6.QtWidgets import QLabel, QMainWindow

    from harrix_swiss_knife.fluent.app_chrome import install_fluent_app_window, refresh_fluent_app_window
    from harrix_swiss_knife.fluent.theme import FluentTheme, enable_fluent_theme

    win = QMainWindow()
    win.setCentralWidget(QLabel("theme-thread"))
    enable_fluent_theme(win)
    install_fluent_app_window(win)
    win.show()
    qapp.processEvents()

    worker = _ShortWorker()
    worker.start()
    FluentTheme.instance().toggle(persist=False)
    refresh_fluent_app_window(win)
    qapp.processEvents()
    assert worker.isRunning()
    worker.wait(2000)
