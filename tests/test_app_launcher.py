"""Tests for tracker app launcher action."""

from __future__ import annotations

import inspect
from contextlib import contextmanager
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife.actions.apps.food import OnFood
from harrix_swiss_knife.actions.apps.habits import OnHabits
from harrix_swiss_knife.apps.finance.main import MainWindow

if TYPE_CHECKING:
    from collections.abc import Iterator

    import pytest


def test_app_launcher_clears_main_window_on_destroyed_callback() -> None:
    """Launcher should drop cached window reference when Qt emits destroyed."""
    action = OnHabits()
    action.main_window = object()
    action._clear_main_window_ref()
    assert action.main_window is None


def test_app_launcher_skips_concurrent_window_creation() -> None:
    """Second execute() while __init__ is running must not spawn another window."""
    action = OnHabits()
    action._is_creating_window = True
    action.execute()
    assert action.main_window is None


def test_habits_launcher_destroys_on_close() -> None:
    """Habits launched from tray should destroy on close like other tracker apps."""
    assert OnHabits.hide_on_close is False
    assert OnFood.hide_on_close is False


def test_app_launcher_shows_loading_toast_while_creating_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Creating a window shows a countdown toast that is closed afterwards."""
    app = QApplication.instance()
    if app is None:
        QApplication([])

    class DummyWindow(QWidget):
        def __init__(self, *, hide_on_close: bool = False) -> None:
            super().__init__()
            del hide_on_close

    started: list[str] = []
    stopped: list[object] = []

    @contextmanager
    def fake_scope(title: str) -> Iterator[None]:
        started.append(title)
        yield
        stopped.append(True)

    monkeypatch.setattr(OnHabits, "get_main_window_class", classmethod(lambda _cls: DummyWindow))
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.app_launcher.app_loading_toast_scope",
        fake_scope,
    )

    action = OnHabits()
    action.execute()
    assert started == ["Habit tracker"]
    assert len(stopped) == 1
    assert action.main_window is not None
    action.main_window.close()


def test_app_launcher_skips_show_when_window_defers_initial_show(monkeypatch: pytest.MonkeyPatch) -> None:
    """Windows with `defer_initial_show` paint themselves after layout is ready."""
    app = QApplication.instance()
    if app is None:
        QApplication([])

    class DeferredWindow(QWidget):
        defer_initial_show = True

        def __init__(self, *, hide_on_close: bool = False) -> None:
            super().__init__()
            del hide_on_close
            self.show_count = 0

        def show(self) -> None:
            self.show_count += 1
            super().show()

    @contextmanager
    def fake_scope(_title: str) -> Iterator[None]:
        yield

    monkeypatch.setattr(OnHabits, "get_main_window_class", classmethod(lambda _cls: DeferredWindow))
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.app_launcher.app_loading_toast_scope",
        fake_scope,
    )

    action = OnHabits()
    action.execute()
    assert action.main_window is not None
    assert action.main_window.show_count == 0
    action.main_window.close()


def test_finance_finish_init_skips_duplicate_exchange_rates_setup() -> None:
    """Exchange rates controls are configured once in _initial_load, not again on show."""
    source = inspect.getsource(MainWindow._finish_window_initialization)
    assert "_setup_exchange_rates_controls" not in source


def test_finance_init_creates_selection_status_before_setup_ui() -> None:
    """Status bar setup reads `_transactions_selection_status_label` during `_setup_ui`."""
    source = inspect.getsource(MainWindow.__init__)
    assert source.index("_transactions_selection_status_label") < source.index("self._setup_ui()")
