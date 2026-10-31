"""App-wide dialog surfaces and Fluent checkbox / radio indicators."""

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
from harrix_swiss_knife.fluent.app_chrome import install_fluent_dialog_chrome
from harrix_swiss_knife.fluent.theme import FLUENT_THEMED_PROPERTY, enable_fluent_theme, is_fluent_themed
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
        _apply_widget_chrome(watched)
        return False


def apply_form_chrome(root: QWidget) -> None:
    """Apply Lucide toggles and dialog surfaces to `root` and its children now."""
    _apply_widget_chrome(root)
    for widget in root.findChildren(QWidget):
        if isinstance(widget, (QCheckBox, QRadioButton)):
            _apply_widget_chrome(widget)


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
    if is_fluent_themed(dialog):
        if not dialog.property(FLUENT_THEMED_PROPERTY):
            enable_fluent_theme(dialog)
        install_fluent_dialog_chrome(dialog)
        return
    apply_white_surface_palette(dialog)


def _apply_widget_chrome(widget: QWidget) -> None:
    if isinstance(widget, QCheckBox):
        apply_lucide_checkbox_style(widget)
    elif isinstance(widget, QRadioButton):
        apply_lucide_radio_style(widget)
    elif isinstance(widget, (QDialog, QMessageBox)):
        _apply_dialog_surface(widget)
