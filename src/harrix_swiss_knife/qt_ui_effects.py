"""Application-wide Qt UI effect settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from harrix_swiss_knife.qt_date_calendar import install_date_calendar_popups
from harrix_swiss_knife.qt_form_chrome import install_form_chrome

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


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
