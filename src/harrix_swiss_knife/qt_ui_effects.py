"""Application-wide Qt UI effect settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def install_ui_effects(app: QApplication) -> None:
    """Disable the combo box popup slide animation.

    On the `windows11` style the animated popup is painted once, then grabbed
    and scrolled open, which reads as a blink every time a combo opens.

    Args:

    - `app` (`QApplication`): Running application.

    """
    app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, enable=False)
