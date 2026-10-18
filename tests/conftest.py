"""Pytest defaults for Harrix Swiss Knife."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.common.subprocess_run import QT_OFFSCREEN_PLATFORM

# Qt tests must not map real windows (they flash during `hsk py check`).
# Assign, do not setdefault: a parent shell may already have set QT_QPA_PLATFORM=windows.
os.environ["QT_QPA_PLATFORM"] = QT_OFFSCREEN_PLATFORM
# Fitness / habit WAVs must not play through the speakers during pytest.
os.environ.setdefault("HSK_MUTE_SOUNDS", "1")


@pytest.fixture(scope="session", autouse=True)
def _destroy_qt_windows_before_shutdown() -> Iterator[None]:
    """Delete top-level Qt windows while `QApplication` is still alive.

    Closed dialogs stay registered until process exit. Destroying them after
    the application object aborts the interpreter on Windows (`0xC0000409`).
    """
    yield
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        return
    for widget in list(app.topLevelWidgets()):
        widget.hide()
        widget.close()
        widget.deleteLater()
    app.processEvents()
