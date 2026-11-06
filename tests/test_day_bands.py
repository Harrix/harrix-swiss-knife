"""Day bands follow the Fluent theme and stay on the record-id header."""

from __future__ import annotations

import warnings

import pytest
from PySide6.QtCore import QThread
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView

from harrix_swiss_knife.apps.common.day_bands import (
    DAY_BAND_ROLE,
    DayBandVerticalHeader,
    day_band_color,
    day_band_id_item,
    install_day_band_vertical_header,
    refresh_day_bands,
    set_day_band,
)
from harrix_swiss_knife.apps.finance.exchange_rates_operations import _disconnect_emitted_signals
from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for table widgets."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        message = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(message)
    return app


def test_day_bands_alternate_and_follow_theme(qapp: QApplication) -> None:
    """Even and odd days differ, and a theme change swaps both fills."""
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.LIGHT, persist=False)
    light_even = day_band_color(0)
    light_odd = day_band_color(1)
    assert light_even.rgb() != light_odd.rgb()
    # Cool bluish bands, not a flat gray plate against the window wallpaper.
    assert light_even.blue() >= light_even.red()
    assert light_odd.blue() >= light_odd.red()
    theme.set_mode(ThemeMode.DARK, persist=False)
    dark_even = day_band_color(0)
    assert dark_even.rgb() != light_even.rgb()
    theme.set_mode(previous, persist=False)


def test_refresh_day_bands_updates_rows_and_ids(qapp: QApplication) -> None:
    """Stored band indexes are repainted, including the id column."""
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.LIGHT, persist=False)
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name"])
    name = QStandardItem("Milk")
    set_day_band(name, day_band_color(1))
    model.appendRow([name])
    model.setVerticalHeaderItem(0, day_band_id_item(7, day_band_color(1)))
    table = QTableView()
    table.setModel(model)
    install_day_band_vertical_header(table)
    theme.set_mode(ThemeMode.DARK, persist=False)
    refresh_day_bands(table)
    assert name.background().color().rgb() == day_band_color(1).rgb()
    header = model.verticalHeaderItem(0)
    assert header is not None
    assert header.data(DAY_BAND_ROLE) == 1
    assert header.background().color().rgb() == day_band_color(1).rgb()
    assert isinstance(table.verticalHeader(), DayBandVerticalHeader)
    theme.set_mode(previous, persist=False)
    table.close()


def test_disconnect_without_slots_is_quiet(qapp: QApplication) -> None:
    """Detaching a worker does not warn about signals that have no slots."""
    assert qapp is not None
    worker = QThread()
    called: list[int] = []
    worker.finished.connect(lambda: called.append(1))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _disconnect_emitted_signals(worker)
    runtime = [item for item in caught if issubclass(item.category, RuntimeWarning)]
    assert runtime == []
    worker.finished.emit()
    assert called == []
