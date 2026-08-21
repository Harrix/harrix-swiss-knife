"""Tests for global BotHub request retry after error or cancel."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QWidget

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub.qt_runner import (
    BothubRequestSpec,
    BothubRequestState,
    _offer_retry_or_finish,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _make_spec(
    *,
    parent: QWidget | None = None,
    on_success: Any = None,
    on_error: Any = None,
    on_cancelled: Any = None,
    offer_retry: bool = True,
    state: BothubRequestState | None = None,
) -> BothubRequestSpec:
    return BothubRequestSpec(
        parent=parent,
        config={},
        prompt_text="prompt",
        on_success=on_success or (lambda _text: None),
        on_error=on_error,
        on_cancelled=on_cancelled,
        offer_retry=offer_retry,
        state=state,
    )


def test_ask_retry_returns_true_for_retry_button(qapp: QApplication) -> None:  # noqa: ARG001
    parent = QWidget()
    clicked: list[QMessageBox] = []

    def _fake_exec(self: QMessageBox) -> int:
        clicked.append(self)
        retry = next(button for button in self.findChildren(QPushButton) if button.text() == "Retry")
        retry.click()
        return 0

    with patch.object(QMessageBox, "exec", _fake_exec):
        assert message_box.ask_retry(parent, "AI Error", "Network failed", critical=True) is True
    assert clicked
    parent.close()


def test_ask_retry_returns_false_for_close_button(qapp: QApplication) -> None:  # noqa: ARG001
    parent = QWidget()

    def _fake_exec(self: QMessageBox) -> int:
        close = next(button for button in self.findChildren(QPushButton) if button.text() == "Close")
        close.click()
        return 0

    with patch.object(QMessageBox, "exec", _fake_exec):
        assert message_box.ask_retry(parent, "Request cancelled", "Cancelled") is False
    parent.close()


def test_offer_retry_close_on_error_calls_on_error(qapp: QApplication) -> None:  # noqa: ARG001
    errors: list[str] = []
    cancelled_calls: list[bool] = []
    state = BothubRequestState()
    state.worker = MagicMock()
    spec = _make_spec(
        on_error=errors.append,
        on_cancelled=lambda: cancelled_calls.append(True),
        state=state,
    )

    with (
        patch("harrix_swiss_knife.integrations.bothub.qt_runner.message_box.ask_retry", return_value=False),
        patch("harrix_swiss_knife.integrations.bothub.qt_runner._start_bothub_request") as start,
    ):
        _offer_retry_or_finish(spec, cancelled=False, message="boom")

    assert errors == ["boom"]
    assert cancelled_calls == []
    assert state.worker is None
    start.assert_not_called()


def test_offer_retry_close_on_cancel_calls_on_cancelled(qapp: QApplication) -> None:  # noqa: ARG001
    errors: list[str] = []
    cancelled_calls: list[bool] = []
    state = BothubRequestState()
    state.worker = MagicMock()
    spec = _make_spec(
        on_error=errors.append,
        on_cancelled=lambda: cancelled_calls.append(True),
        state=state,
    )

    with (
        patch("harrix_swiss_knife.integrations.bothub.qt_runner.message_box.ask_retry", return_value=False),
        patch("harrix_swiss_knife.integrations.bothub.qt_runner._start_bothub_request") as start,
    ):
        _offer_retry_or_finish(spec, cancelled=True, message="Request cancelled by user.")

    assert errors == []
    assert cancelled_calls == [True]
    assert state.worker is None
    start.assert_not_called()


def test_offer_retry_restarts_same_spec(qapp: QApplication) -> None:  # noqa: ARG001
    errors: list[str] = []
    state = BothubRequestState()
    state.worker = MagicMock()
    spec = _make_spec(on_error=errors.append, state=state)

    with (
        patch("harrix_swiss_knife.integrations.bothub.qt_runner.message_box.ask_retry", return_value=True),
        patch(
            "harrix_swiss_knife.integrations.bothub.qt_runner._start_bothub_request",
            return_value=True,
        ) as start,
    ):
        _offer_retry_or_finish(spec, cancelled=False, message="timeout")

    assert errors == []
    start.assert_called_once_with(spec)


def test_offer_retry_disabled_finishes_immediately(qapp: QApplication) -> None:  # noqa: ARG001
    errors: list[str] = []
    spec = _make_spec(on_error=errors.append, offer_retry=False)

    with (
        patch("harrix_swiss_knife.integrations.bothub.qt_runner.message_box.ask_retry") as ask,
        patch("harrix_swiss_knife.integrations.bothub.qt_runner._start_bothub_request") as start,
    ):
        _offer_retry_or_finish(spec, cancelled=False, message="boom")

    assert errors == ["boom"]
    ask.assert_not_called()
    start.assert_not_called()


def test_offer_retry_failed_restart_finishes_with_error(qapp: QApplication) -> None:  # noqa: ARG001
    errors: list[str] = []
    state = BothubRequestState()
    state.worker = MagicMock()
    spec = _make_spec(on_error=errors.append, state=state)

    with (
        patch("harrix_swiss_knife.integrations.bothub.qt_runner.message_box.ask_retry", return_value=True),
        patch(
            "harrix_swiss_knife.integrations.bothub.qt_runner._start_bothub_request",
            return_value=False,
        ),
    ):
        _offer_retry_or_finish(spec, cancelled=False, message="boom")

    assert errors == ["boom"]
    assert state.worker is None
