"""Tests for Explorer file drops on widgets and DragOnly icon lists."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QEvent, QMimeData, QPoint, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import QApplication, QListWidget

from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import install_url_drop_handlers


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _mime_for_path(path: Path) -> QMimeData:
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(path.resolve()))])
    return mime


def _drag_enter(mime: QMimeData) -> QDragEnterEvent:
    return QDragEnterEvent(
        QPoint(12, 12),
        Qt.DropAction.CopyAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def _drag_move(mime: QMimeData) -> QDragMoveEvent:
    return QDragMoveEvent(
        QPoint(12, 12),
        Qt.DropAction.CopyAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def _drop(mime: QMimeData) -> QDropEvent:
    return QDropEvent(
        QPoint(12, 12),
        Qt.DropAction.CopyAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        QEvent.Type.Drop,
    )


def _drag_only_list() -> QListWidget:
    widget = QListWidget()
    widget.setDragDropMode(QListWidget.DragDropMode.DragOnly)
    return widget


def test_drag_only_list_accepts_filtered_file_drop(qapp: QApplication, tmp_path: Path) -> None:
    assert qapp is not None
    svg = tmp_path / "building__shed.svg"
    svg.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")

    received: list[list[str]] = []
    widget = _drag_only_list()
    install_url_drop_handlers(
        widget,
        received.append,
        filter_path=lambda path: Path(path).suffix.casefold() == ".svg",
    )

    mime = _mime_for_path(svg)
    enter = _drag_enter(mime)
    assert qapp.sendEvent(widget.viewport(), enter)
    assert enter.isAccepted()

    move = _drag_move(mime)
    assert qapp.sendEvent(widget.viewport(), move)
    assert move.isAccepted()

    drop = _drop(mime)
    assert qapp.sendEvent(widget.viewport(), drop)
    qapp.processEvents()
    assert len(received) == 1
    assert Path(received[0][0]) == svg


def test_drag_only_list_rejects_filtered_out_file(qapp: QApplication, tmp_path: Path) -> None:
    assert qapp is not None
    png = tmp_path / "photo.png"
    png.write_bytes(b"png")
    widget = _drag_only_list()
    install_url_drop_handlers(
        widget,
        lambda _paths: None,
        filter_path=lambda path: Path(path).suffix.casefold() == ".svg",
    )
    mime = _mime_for_path(png)
    enter = _drag_enter(mime)
    qapp.sendEvent(widget.viewport(), enter)
    assert not enter.isAccepted()
