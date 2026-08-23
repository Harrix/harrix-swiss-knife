"""Tests for the tray single-instance socket."""

from __future__ import annotations

import logging
import uuid
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.app_startup import run_tray_application
from harrix_swiss_knife.single_instance import (
    SingleInstance,
    acquire_tray_instance,
    default_server_name,
    release_held_instance,
    restore_held_instance,
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


def _unique_name() -> str:
    return f"hsk-test-{uuid.uuid4().hex}"


def test_default_server_name_is_per_user() -> None:
    name = default_server_name()
    assert name.startswith("harrix-swiss-knife-")
    assert " " not in name


def test_second_claim_notifies_first(qapp: QApplication) -> None:
    name = _unique_name()
    seen: list[bool] = []
    first = SingleInstance(name)
    second = SingleInstance(name)
    try:
        assert first.try_claim() is True
        first.activate_requested.connect(lambda: seen.append(True))
        assert second.try_claim() is False
        for _ in range(50):
            qapp.processEvents()
            if seen:
                break
        assert seen
    finally:
        first.release()
        second.release()


def test_release_allows_a_new_claim(qapp: QApplication) -> None:  # noqa: ARG001
    name = _unique_name()
    first = SingleInstance(name)
    second = SingleInstance(name)
    try:
        assert first.try_claim() is True
        first.release()
        assert second.try_claim() is True
    finally:
        first.release()
        second.release()


def test_acquire_tray_instance_notifies_and_release_clears_hold(qapp: QApplication) -> None:
    name = _unique_name()
    called: list[int] = []
    first = acquire_tray_instance(lambda: called.append(1), name=name)
    assert first is not None
    try:
        second = acquire_tray_instance(lambda: None, name=name)
        assert second is None
        for _ in range(50):
            qapp.processEvents()
            if called:
                break
        assert called
    finally:
        release_held_instance()
    third = acquire_tray_instance(lambda: None, name=name)
    try:
        assert third is not None
    finally:
        release_held_instance()


def test_restore_held_instance_reclaims_socket(qapp: QApplication) -> None:  # noqa: ARG001
    name = _unique_name()
    first = acquire_tray_instance(lambda: None, name=name)
    assert first is not None
    released = release_held_instance()
    assert released is first
    assert restore_held_instance(first) is True
    try:
        other = SingleInstance(name)
        try:
            assert other.try_claim() is False
        finally:
            other.release()
    finally:
        release_held_instance()


def test_run_tray_application_exits_when_another_instance_owns_socket() -> None:
    with (
        patch("harrix_swiss_knife.app_startup.h.dev.config_load", return_value={}),
        patch("harrix_swiss_knife.app_startup.QApplication") as qapp_cls,
        patch("harrix_swiss_knife.app_startup.acquire_tray_instance", return_value=None),
        patch("harrix_swiss_knife.app_startup.install_safe_qt_translate"),
        patch("harrix_swiss_knife.app_startup.QIcon"),
    ):
        qapp_cls.return_value = MagicMock()
        rc = run_tray_application(logging.getLogger("test_single_instance"), main_menu_cls=MagicMock)
    assert rc == 0
