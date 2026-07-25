"""Tests that cancellable BotHub toasts can receive input above modal dialogs."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.integrations.bothub.qt_runner import _resolve_toast_parent
from harrix_swiss_knife.toast_cancellable_http_notification import ToastCancellableHttpNotification


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_cancellable_toast_is_application_modal(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastCancellableHttpNotification("Requesting BotHub…")
    assert toast.windowModality() == Qt.WindowModality.ApplicationModal
    toast.close()


def test_resolve_toast_parent_prefers_explicit_parent(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = QDialog()
    assert _resolve_toast_parent(dialog) is dialog
    dialog.close()


def test_resolve_toast_parent_falls_back_to_active_modal(qapp: QApplication) -> None:  # noqa: ARG001
    modal = QDialog()
    modal.setWindowModality(Qt.WindowModality.ApplicationModal)
    modal.show()
    QApplication.processEvents()

    assert QApplication.activeModalWidget() is modal
    assert _resolve_toast_parent(None) is modal

    modal.close()


def test_cancellable_toast_parented_under_modal_can_be_focused(qapp: QApplication) -> None:  # noqa: ARG001
    modal = QDialog()
    modal.setWindowModality(Qt.WindowModality.ApplicationModal)
    modal.show()
    QApplication.processEvents()

    toast = ToastCancellableHttpNotification("Requesting BotHub…", parent=modal)
    toast.present()
    QApplication.processEvents()

    assert toast.parent() is modal
    assert toast.windowModality() == Qt.WindowModality.ApplicationModal
    assert toast.isVisible()
    assert toast.hasFocus() or toast.isActiveWindow()

    toast.close()
    modal.close()
