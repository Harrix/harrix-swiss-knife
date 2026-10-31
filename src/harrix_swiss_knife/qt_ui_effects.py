"""Application-wide Qt UI effect settings."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QApplication, QDateEdit

from harrix_swiss_knife.qt_date_calendar import install_date_calendar_popups, install_date_edit_double_click_popup
from harrix_swiss_knife.qt_form_chrome import apply_form_chrome, install_form_chrome

if TYPE_CHECKING:
    from collections.abc import Generator

    from PySide6.QtWidgets import QWidget

# Install order of the app-wide Python polish filters (see `install_app_fonts`, `install_ui_effects`).
_POLISH_FILTER_PROPS = ("_hskUiFontScaleFilter", "_hskDateCalendarFilter", "_hskFormChromeFilter")
_suspend_depth = 0


def install_ui_effects(app: QApplication) -> None:
    """Disable combo popup slide animation and install shared form chrome.

    On the `windows11` style the animated popup is painted once, then grabbed
    and scrolled open, which reads as a blink every time a combo opens.

    Also paints Lucide checkbox / radio indicators and white dialog surfaces.

    Args:

    - `app` (`QApplication`): Running application.

    """
    app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, enable=False)
    install_date_calendar_popups(app)
    install_form_chrome(app)


@contextmanager
def suspended_polish_filters(root: QWidget) -> Generator[None]:
    """Detach the app-wide polish filters while `root` is restyled in bulk.

    Every `setStyleSheet` on a container re-polishes its whole subtree, and each
    event of each child goes through the Python application filters. Restyling a
    tracker window that way costs seconds. The filters' work is replayed once on
    `root` afterwards.

    Args:

    - `root` (`QWidget`): Window or dialog that is about to be restyled.

    """
    global _suspend_depth  # noqa: PLW0603
    app = QApplication.instance()
    filters: list[QObject] = []
    if _suspend_depth == 0 and isinstance(app, QApplication):
        for prop in _POLISH_FILTER_PROPS:
            event_filter = app.property(prop)
            if isinstance(event_filter, QObject):
                app.removeEventFilter(event_filter)
                filters.append(event_filter)
    _suspend_depth += 1
    try:
        yield
    finally:
        _suspend_depth -= 1
        if isinstance(app, QApplication):
            for event_filter in filters:
                app.installEventFilter(event_filter)
        if filters:
            _replay_polish_filters(root)


def _replay_polish_filters(root: QWidget) -> None:
    from harrix_swiss_knife.qt_app_font import apply_ui_font_scale  # noqa: PLC0415

    apply_ui_font_scale(root)
    apply_form_chrome(root)
    for date_edit in root.findChildren(QDateEdit):
        install_date_edit_double_click_popup(date_edit)
