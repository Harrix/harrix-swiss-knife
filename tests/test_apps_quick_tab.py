"""Tests for Quick-tab startup preference in Finance, Food, and Fitness."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import QApplication, QCheckBox, QTabWidget, QVBoxLayout, QWidget

from harrix_swiss_knife.apps.common.apps_config import (
    get_open_quick_tab_on_startup,
    open_quick_tab_on_startup_key,
    set_open_quick_tab_on_startup,
    startup_tab_index,
)
from harrix_swiss_knife.apps.common.quick_tab_startup import install_open_quick_tab_checkbox

if TYPE_CHECKING:
    from pathlib import Path


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_startup_tab_index_uses_quick_or_second() -> None:
    """Checked preference opens tab 0; unchecked opens tab 1."""
    assert startup_tab_index(open_quick=True) == 0
    assert startup_tab_index(open_quick=False) == 1


def test_get_open_quick_tab_on_startup_defaults_and_reads_bool() -> None:
    """Missing keys default to True; only a real bool is accepted."""
    assert get_open_quick_tab_on_startup({}, "finance") is True
    assert get_open_quick_tab_on_startup({"apps": {"open_quick_tab_on_startup_food": False}}, "food") is False
    assert get_open_quick_tab_on_startup({"apps": {"open_quick_tab_on_startup_fitness": "no"}}, "fitness") is True


def test_set_open_quick_tab_on_startup_writes_per_app_key(tmp_path: Path) -> None:
    """Each tracker app stores its own Quick-tab flag under `apps`."""
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"editor-notes": "code", "apps": {"initial_count": 10}}), encoding="utf-8")
    live: dict[str, Any] = {"apps": {"initial_count": 10}}
    set_open_quick_tab_on_startup("finance", enabled=False, config=live, config_path=str(path))
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["apps"]["open_quick_tab_on_startup_finance"] is False
    assert written["apps"]["initial_count"] == 10
    assert written["editor-notes"] == "code"
    assert live["apps"][open_quick_tab_on_startup_key("finance")] is False
    set_open_quick_tab_on_startup("food", enabled=True, config_path=str(path))
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["apps"]["open_quick_tab_on_startup_food"] is True
    assert written["apps"]["open_quick_tab_on_startup_finance"] is False


def test_install_open_quick_tab_checkbox_selects_second_tab() -> None:
    """Unchecked preference opens the second tab and shows a checkbox."""
    assert _qapp() is not None
    window = QWidget()
    window._app_config = {"apps": {"open_quick_tab_on_startup_fitness": False}}
    tabs = QTabWidget(window)
    quick = QWidget()
    second = QWidget()
    layout = QVBoxLayout(quick)
    tabs.addTab(quick, "Quick")
    tabs.addTab(second, "Sets")
    checkbox = install_open_quick_tab_checkbox(
        window,
        app="fitness",
        tab_layout=layout,
        tab_widget=tabs,
    )
    assert isinstance(checkbox, QCheckBox)
    assert not checkbox.isChecked()
    assert tabs.currentIndex() == 1
    window.close()
