"""Tests for installer wizard cancel-while-installing confirmation."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from harrix_swiss_knife.installer.wizard import InstallerWizard


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_is_install_running_false_without_worker(qapp: QApplication) -> None:  # noqa: ARG001
    wizard = InstallerWizard("online")
    assert wizard.is_install_running() is False


def test_is_install_running_true_when_worker_active(qapp: QApplication) -> None:  # noqa: ARG001
    wizard = InstallerWizard("online")
    worker = MagicMock()
    worker.isRunning.return_value = True
    wizard.progress_page._worker = worker
    assert wizard.is_install_running() is True
    worker.isRunning.return_value = False
    assert wizard.is_install_running() is False


def test_confirm_abort_skips_dialog_when_idle(qapp: QApplication) -> None:  # noqa: ARG001
    wizard = InstallerWizard("online")
    with patch.object(QMessageBox, "question") as question:
        assert wizard._confirm_abort_if_installing() is True
        question.assert_not_called()


def test_confirm_abort_asks_when_installing(qapp: QApplication) -> None:  # noqa: ARG001
    wizard = InstallerWizard("online")
    worker = MagicMock()
    worker.isRunning.return_value = True
    wizard.progress_page._worker = worker
    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No) as question:
        assert wizard._confirm_abort_if_installing() is False
        question.assert_called_once()
        message = question.call_args.args[2]
        assert "still in progress" in message
        assert "removed manually" in message
    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
        assert wizard._confirm_abort_if_installing() is True
