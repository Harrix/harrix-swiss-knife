"""App-wide white dialog surfaces and Lucide checkbox / radio indicators."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QMessageBox,
    QRadioButton,
    QWidget,
)

from harrix_swiss_knife.apps.common.ui_chrome import apply_white_surface_palette
from harrix_swiss_knife.qt_lucide_checkbox import (
    apply_lucide_checkbox_style,
    apply_lucide_radio_style,
)

_PROP = "_hskFormChromeFilter"


class _FormChromeFilter(QObject):
    """Polish Lucide toggles and white-surface modal forms as widgets appear."""

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() != QEvent.Type.Polish or not isinstance(watched, QWidget):
            return False
        if isinstance(watched, QCheckBox):
            apply_lucide_checkbox_style(watched)
        elif isinstance(watched, QRadioButton):
            apply_lucide_radio_style(watched)
        elif isinstance(watched, (QDialog, QMessageBox)):
            _apply_dialog_surface(watched)
        return False


def install_form_chrome(app: QApplication) -> None:
    """Install the shared form chrome polish filter once on `app`."""
    if not isinstance(app, QApplication):
        return
    existing = app.property(_PROP)
    if isinstance(existing, _FormChromeFilter):
        return
    event_filter = _FormChromeFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty(_PROP, event_filter)


def _apply_dialog_surface(dialog: QWidget) -> None:
    if dialog.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground):
        return
    apply_white_surface_palette(dialog)
