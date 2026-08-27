"""Tests for shrinkable tab-page scroll wrapping."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QHBoxLayout, QTabWidget, QWidget

from harrix_swiss_knife.apps.common.widgets.shrinkable_scroll_area import (
    wrap_tab_pages_in_shrinkable_scroll,
    wrap_widget_contents_in_shrinkable_scroll,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_wrap_widget_contents_allows_host_to_shrink(qapp: QApplication) -> None:
    assert qapp is not None
    host = QWidget()
    layout = QHBoxLayout(host)
    wide = QWidget()
    wide.setMinimumWidth(800)
    layout.addWidget(wide)
    scroll = wrap_widget_contents_in_shrinkable_scroll(host)
    assert scroll.minimumSizeHint().width() < 800
    assert host.minimumSizeHint().width() < 800
    assert scroll.widget() is not None
    assert scroll.widget().minimumSizeHint().width() >= 800
    host.close()


def test_wrap_tab_pages_in_shrinkable_scroll(qapp: QApplication) -> None:
    assert qapp is not None
    tabs = QTabWidget()
    page = QWidget()
    layout = QHBoxLayout(page)
    wide = QWidget()
    wide.setMinimumWidth(900)
    layout.addWidget(wide)
    tabs.addTab(page, "Sets")
    wrap_tab_pages_in_shrinkable_scroll(tabs)
    assert page.minimumSizeHint().width() < 900
    tabs.close()
