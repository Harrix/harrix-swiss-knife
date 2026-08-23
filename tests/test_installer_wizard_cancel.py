"""Tests for installer wizard cancel-while-installing confirmation and progress page."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from harrix_swiss_knife.installer.wizard import InstallerWizard, ProgressPage


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


def test_progress_page_stays_incomplete_after_error(qapp: QApplication) -> None:  # noqa: ARG001
    page = ProgressPage("online")
    with patch.object(QMessageBox, "critical"):
        page._on_err("Git install failed")
    assert page.isComplete() is False
    with patch.object(page, "_retry_install"):
        assert page.validatePage() is False


def test_begin_if_needed_clears_finished_worker(qapp: QApplication) -> None:  # noqa: ARG001
    wizard = InstallerWizard("online")
    page = wizard.progress_page
    stale_worker = MagicMock()
    stale_worker.isRunning.return_value = False
    page._worker = stale_worker
    with patch.object(page, "_start_worker") as start_worker:
        page._begin_if_needed()
        start_worker.assert_called_once()


def test_progress_page_retry_starts_worker(qapp: QApplication) -> None:  # noqa: ARG001
    wizard = InstallerWizard("online")
    page = wizard.progress_page
    with patch.object(page, "_start_worker") as start_worker:
        page._retry_install()
        start_worker.assert_called_once()
