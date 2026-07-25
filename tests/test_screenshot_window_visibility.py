"""Tests for screenshot window conceal/restore without closing modal dialogs."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QWidget

from harrix_swiss_knife.screenshot.window_visibility import hide_app_windows, restore_app_windows


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_hide_app_windows_keeps_modal_dialog_exec_alive(qapp: QApplication) -> None:  # noqa: ARG001
    """Modal dialogs must stay accepted/open after conceal — hide() would reject exec()."""
    dialog = QDialog()
    dialog.setModal(True)
    dialog.setWindowOpacity(1.0)
    dialog.show()
    QApplication.processEvents()

    concealed = hide_app_windows()
    assert any(item.widget is dialog and item.mode == "opacity" for item in concealed)
    assert dialog.isVisible()
    assert dialog.windowOpacity() == 0.0
    assert dialog.result() == 0  # not finished/rejected
    # Invisible modal must not keep ApplicationModal (blocks shutter / beeps).
    assert dialog.windowModality() == Qt.WindowModality.NonModal
    assert not dialog.isModal()
    assert dialog.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    restore_app_windows(concealed)
    assert dialog.windowOpacity() == 1.0
    assert dialog.isVisible()
    assert dialog.result() == 0
    assert dialog.windowModality() == Qt.WindowModality.ApplicationModal
    assert dialog.isModal()
    assert not dialog.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    dialog.close()


def test_hide_app_windows_hides_non_modal_top_level(qapp: QApplication) -> None:  # noqa: ARG001
    window = QWidget()
    window.setWindowTitle("non-modal-test")
    window.show()
    QApplication.processEvents()

    concealed = hide_app_windows()
    match = next(item for item in concealed if item.widget is window)
    assert match.mode == "hide"
    assert not window.isVisible()

    restore_app_windows(concealed)
    assert window.isVisible()
    window.close()
